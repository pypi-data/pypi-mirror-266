from naludaq.communication import AnalogRegisters

from .default import TriggerController


class TriggerControllerTrbhm(TriggerController):
    """Trigger controller for TRBHM boards."""

    def __init__(self, board):
        super().__init__(board)

        self._num_chips = board.params.get("num_chips", 2)
        self._num_trig_chans_per_chip = board.params.get("num_trig_chans_per_chip", 4)

    def write_triggers(self):
        """Write the trigger values to the hardware.

        This writes the current set triggers to the hardware.
        By setting the trigger_offsets or the trigger_values
        this function is called automatically and the hardware is updated.
        """
        self._set_trigger_thresholds()
        self._set_wbiases()

        return True

    def _set_trigger_thresholds(self):
        """Sets the trigger values to those in the board object and writes to hardware."""
        trigger_values = self.board.trigger_values
        self._write_analog_registers_per_chip("trigger_threshold_{:02}", trigger_values)

    def _set_wbiases(self):
        """Set the wbias registers based on the board trigger values"""
        wbias = [self._wbias if x > 0 else 0 for x in self.board.trigger_values]
        self._write_analog_registers_per_chip("wbias_{:02}", wbias)

    def _write_analog_registers_per_chip(self, reg_name_format: str, values: list):
        """Write analog registers with a given register name format using the
        values provided. Writes values to both chips individually.

        Args:
            reg_name_format (str): register name format string, must take one integer argument.
            values (list): list of values to write. Should be all 8 values across both chips.
        """
        for chip in range(self.board.available_chips):
            for idx in range(self._num_trig_chans_per_chip):
                name = reg_name_format.format(idx)
                val = values[idx + chip * self._num_trig_chans_per_chip]
                AnalogRegisters(self.board, [chip]).write(name, val)
