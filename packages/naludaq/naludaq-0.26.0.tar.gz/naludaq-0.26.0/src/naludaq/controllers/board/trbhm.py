"""
"""
from logging import getLogger

from naludaq.communication import ControlRegisters, DigitalRegisters

from .default import BoardController

LOGGER = getLogger("naludaq.board_controller_trbhm")


class TrbhmBoardController(BoardController):
    """Special board controller for TRBHM."""

    def read_scalar(self, channel: int) -> int:
        """Read the scalar for the given channel"""
        channels_per_chip = self.board.channels // self.board.available_chips
        relative_channel = channel % channels_per_chip
        chip = channel // channels_per_chip
        return self._read_scalar_inner(chip, relative_channel)

    def _read_scalar_inner(self, chip: int, relative_channel: int) -> int:
        """Read the scalar for the given channel.

        This is the inner function that actually reads the scalar.
        It is called by `read_scalar` and should not be called directly.
        """
        name = self.get_scal_name(relative_channel)
        scal = self._read_digital_register(name, chips=chip)
        try:
            scalhigh = self._read_digital_register("scalhigh", chips=chip)
        except (KeyError, AttributeError):
            scalhigh = 0
        shift_amt = DigitalRegisters(self.board).registers[name]["bitwidth"]
        scal += scalhigh << shift_amt

        return scal

    def toggle_trigger(self):
        """Toggles the ext trigger using software.

        For TRBHM the wait between separate register writes is too long, and
        toggling the trigger too slowly results in too many events coming back
        and filling the FIFO, causing malformed events. This method instead
        sends the register writes all as one string.
        """
        cr = ControlRegisters(self.board)

        wait_cmd = "AE000001"
        exttrig_high_cmd = cr.generate_write("exttrig", True)
        exttrig_low_cmd = cr.generate_write("exttrig", False)
        toggle_cmd = wait_cmd + exttrig_high_cmd + exttrig_low_cmd
        self._send_command(toggle_cmd)

    def set_loopback_enabled(self, enabled: bool):
        """Set whether serial loopback is enabled.

        Loopback can safely be disabled during most of the operations with the board.
        Loopback **must** be disabled when communicating over the serial interface.
        If serial communication with the ASIC is intended then this should run during startup and only be enabled as needed.

        Args:
            enabled (bool): True to enable loopback.

        Raises:
            TypeError if enabled is not a bool.
        """
        if not isinstance(enabled, bool):
            raise TypeError("Argument must be bool")
        OFF = "B0900002"
        ON = "B0900003"
        cmd = ON if enabled else OFF
        self._send_command(cmd)
