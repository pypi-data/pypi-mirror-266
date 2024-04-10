"""
SCAN PLUGINS

All new scans should be derived from ScanBase. ScanBase provides various methods that can be customized and overriden
but they are executed in a specific order:

- self.initialize                        # initialize the class if needed
- self.read_scan_motors                  # used to retrieve the start position (and the relative position shift if needed)
- self.prepare_positions                 # prepare the positions for the scan. The preparation is split into multiple sub fuctions:
    - self._calculate_positions          # calculate the positions
    - self._set_positions_offset         # apply the previously retrieved scan position shift (if needed)
    - self._check_limits                 # tests to ensure the limits won't be reached
- self.open_scan                         # send an open_scan message including the scan name, the number of points and the scan motor names
- self.stage                             # stage all devices for the upcoming acquisiton
- self.run_baseline_readings             # read all devices to get a baseline for the upcoming scan
- self.scan_core                         # run a loop over all position
    - self._at_each_point(ind, pos)      # called at each position with the current index and the target positions as arguments
- self.finalize                          # clean up the scan, e.g. move back to the start position; wait everything to finish
- self.unstage                           # unstage all devices that have been staged before
- self.cleanup                           # send a close scan message and perform additional cleanups if needed
"""

import time

import numpy as np

from bec_lib import MessageEndpoints, bec_logger, messages
from scan_server.errors import ScanAbortion
from scan_server.scans import SyncFlyScanBase

logger = bec_logger.logger


class FlomniFermatScan(SyncFlyScanBase):
    scan_name = "flomni_fermat_scan"
    scan_report_hint = "table"
    scan_type = "fly"
    required_kwargs = ["fov_size", "exp_time", "step", "angle"]
    arg_input = {}
    arg_bundle_size = {"bundle": len(arg_input), "min": None, "max": None}

    def __init__(
        self,
        fovx: float,
        fovy: float,
        cenx: float,
        ceny: float,
        exp_time: float,
        step: float,
        zshift: float,
        angle: float = None,
        corridor_size: float = 3,
        parameter: dict = None,
        **kwargs,
    ):
        """
        A flomni scan following Fermat's spiral.

        Args:
            fovx(float) [um]: Fov in the piezo plane (i.e. piezo range). Max 200 um
            fovy(float) [um]: Fov in the piezo plane (i.e. piezo range). Max 100 um
            cenx(float) [mm]: center position in x.
            ceny(float) [mm]: center position in y.
            exp_time(float) [s]: exposure time
            step(float) [um]: stepsize
            zshift(float) [um]: shift in z
            angle(float) [deg]: rotation angle (will rotate first)
            corridor_size(float) [um]: corridor size for the corridor optimization. Default 3 um

        Returns:

        Examples:
            >>> scans.flomni_fermat_scan(fovx=20, fovy=25, cenx=0.02, ceny=0, zshift=0, angle=0, step=0.5, exp_time=0.01)
        """

        super().__init__(parameter=parameter, **kwargs)
        self.axis = []
        self.fovx = fovx
        self.fovy = fovy
        self.cenx = cenx
        self.ceny = ceny
        self.exp_time = exp_time
        self.step = step
        self.zshift = zshift
        self.angle = angle
        self.optim_trajectory = "corridor"
        self.optim_trajectory_corridor = corridor_size
        if self.fovy > 100:
            raise ScanAbortion("The FOV in y must be smaller than 100 um.")
        if self.fovx > 200:
            raise ScanAbortion("The FOV in x must be smaller than 200 um.")
        if self.zshift > 100:
            logger.warning("The zshift is larger than 100 um. It will be limited to 100 um.")
            self.zshift = 100
        if self.zshift < -100:
            logger.warning("The zshift is smaller than -100 um. It will be limited to -100 um.")
            self.zshift = -100

    def initialize(self):
        self.scan_motors = []
        self.update_readout_priority()

    def _optimize_trajectory(self):
        self.positions = self.optimize_corridor(
            self.positions, corridor_size=self.optim_trajectory_corridor
        )

    @property
    def monitor_sync(self):
        return "rt_flomni"

    def reverse_trajectory(self):
        """
        Reverse the trajectory. Every other scan should be reversed to
        shorten the movement time. In order to keep the last state, even if the
        server is restarted, the state is stored in a global variable in redis.
        """
        producer = self.device_manager.producer
        msg = producer.get(MessageEndpoints.global_vars("reverse_flomni_trajectory"))
        if msg:
            val = msg.content.get("value", False)
        else:
            val = False
        producer.set(
            MessageEndpoints.global_vars("reverse_flomni_trajectory"),
            messages.VariableMessage(value=(not val)),
        )
        return val

    def prepare_positions(self):
        self._calculate_positions()
        self._optimize_trajectory()
        flip_axes = self.reverse_trajectory()
        if flip_axes:
            self.positions = np.flipud(self.positions)

        self.num_pos = len(self.positions)
        self._check_min_positions()

    def _check_min_positions(self):
        if self.num_pos < 20:
            raise ScanAbortion(
                f"The number of positions must exceed 20. Currently: {self.num_pos}."
            )

    def _prepare_setup(self):
        yield from self.stubs.send_rpc_and_wait("rtx", "controller.clear_trajectory_generator")
        yield from self.flomni_rotation(self.angle)

        yield from self.stubs.send_rpc_and_wait("rty", "set", self.positions[0][1])

    def _prepare_setup_part2(self):
        yield from self.stubs.wait(wait_type="move", device="fsamroy", wait_group="flomni_rotation")
        yield from self.stubs.set(
            device="rtx", value=self.positions[0][0], wait_group="prepare_setup_part2"
        )
        yield from self.stubs.set(
            device="rtz", value=self.positions[0][2], wait_group="prepare_setup_part2"
        )
        yield from self.stubs.send_rpc_and_wait("rtx", "controller.laser_tracker_on")
        yield from self.stubs.wait(
            wait_type="move", device=["rtx", "rtz"], wait_group="prepare_setup_part2"
        )
        yield from self._transfer_positions_to_flomni()
        yield from self.stubs.send_rpc_and_wait(
            "rtx", "controller.move_samx_to_scan_region", self.fovx, self.cenx
        )

    def flomni_rotation(self, angle):
        # get last setpoint (cannot be based on pos get because they will deviate slightly)
        fsamroy_current_setpoint = yield from self.stubs.send_rpc_and_wait(
            "fsamroy", "user_setpoint.get"
        )
        if angle == fsamroy_current_setpoint:
            logger.info("No rotation required")
        else:
            logger.info("Rotating to requested angle")
            yield from self.stubs.scan_report_instruction(
                {
                    "readback": {
                        "RID": self.metadata["RID"],
                        "devices": ["fsamroy"],
                        "start": [fsamroy_current_setpoint],
                        "end": [angle],
                    }
                }
            )
            yield from self.stubs.set(device="fsamroy", value=angle, wait_group="flomni_rotation")

    def _transfer_positions_to_flomni(self):
        yield from self.stubs.send_rpc_and_wait(
            "rtx", "controller.add_pos_to_scan", self.positions.tolist()
        )

    def _calculate_positions(self):
        self.positions = self.get_flomni_fermat_spiral_pos(
            -np.abs(self.fovx / 2),
            np.abs(self.fovx / 2),
            -np.abs(self.fovy / 2),
            np.abs(self.fovy / 2),
            step=self.step,
            spiral_type=0,
            center=False,
        )

    def get_flomni_fermat_spiral_pos(
        self, m1_start, m1_stop, m2_start, m2_stop, step=1, spiral_type=0, center=False
    ):
        """
        Calculate positions for a Fermat spiral scan.

        Args:
            m1_start(float): start position in m1
            m1_stop(float): stop position in m1
            m2_start(float): start position in m2
            m2_stop(float): stop position in m2
            step(float): stepsize
            spiral_type(int): 0 for traditional Fermat spiral
            center(bool): whether to include the center position

        Returns:
            positions(array): positions
        """
        positions = []
        phi = 2 * np.pi * ((1 + np.sqrt(5)) / 2.0) + spiral_type * np.pi

        start = int(not center)

        length_axis1 = np.abs(m1_stop - m1_start)
        length_axis2 = np.abs(m2_stop - m2_start)
        n_max = int(length_axis1 * length_axis2 * 3.2 / step / step)

        z_pos = self.zshift

        for ii in range(start, n_max):
            radius = step * 0.57 * np.sqrt(ii)
            # FOV is restructed below at check pos in range
            if abs(radius * np.sin(ii * phi)) > length_axis1 / 2:
                continue
            if abs(radius * np.cos(ii * phi)) > length_axis2 / 2:
                continue
            x = radius * np.sin(ii * phi)
            y = radius * np.cos(ii * phi)
            positions.append([x + self.cenx, y + self.ceny, z_pos])
        left_lower_corner = [
            min(m1_start, m1_stop) + self.cenx,
            min(m2_start, m2_stop) + self.ceny,
            z_pos,
        ]
        right_upper_corner = [
            max(m1_start, m1_stop) + self.cenx,
            max(m2_start, m2_stop) + self.ceny,
            z_pos,
        ]
        positions.append(left_lower_corner)
        positions.append(right_upper_corner)
        return np.array(positions)

    def scan_core(self):
        # use a device message to receive the scan number and
        # scan ID before sending the message to the device server
        yield from self.stubs.kickoff(device="rtx")
        while True:
            yield from self.stubs.read_and_wait(group="primary", wait_group="readout_primary")
            status = self.device_manager.producer.get(MessageEndpoints.device_status("rt_scan"))
            if status:
                status_id = status.content.get("status", 1)
                request_id = status.metadata.get("RID")
                if status_id == 0 and self.metadata.get("RID") == request_id:
                    break
                if status_id == 2 and self.metadata.get("RID") == request_id:
                    raise ScanAbortion(
                        "An error occured during the flomni readout:"
                        f" {status.metadata.get('error')}"
                    )

            time.sleep(1)
            logger.debug("reading monitors")
        # yield from self.device_rpc("rtx", "controller.kickoff")

    def return_to_start(self):
        """return to the start position"""
        # in flomni, we need to move to the start position of the next scan
        yield from self.stubs.send_rpc_and_wait("rtx", "set", self.positions[-1][0])
        yield from self.stubs.send_rpc_and_wait("rty", "set", self.positions[-1][1])
        yield from self.stubs.send_rpc_and_wait("rtz", "set", self.positions[-1][2])

    def run(self):
        self.initialize()
        yield from self.read_scan_motors()
        self.prepare_positions()
        yield from self._prepare_setup()
        yield from self.open_scan()
        yield from self.stage()
        yield from self.run_baseline_reading()
        yield from self._prepare_setup_part2()
        yield from self.scan_core()
        yield from self.finalize()
        yield from self.unstage()
        yield from self.cleanup()
