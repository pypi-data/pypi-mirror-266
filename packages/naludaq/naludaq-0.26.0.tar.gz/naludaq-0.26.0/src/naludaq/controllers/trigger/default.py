"""Trigger controller.

The trigger controller is an interface to access and operate the
trigger functionality in the Nalu hardware.
The trigger is active when the chip is in the trigger mode,
by setting BoardController(board).start_readout(*args) where trig
is set to "ext" or "imm".

The trigger is operated by two variables, offset and value.
The value is the ADC threshold value of the trigger.
The offset is an offset from the 0, by setting offset it's possible to
fine-tune the trigger since the needed value is now smaller.

Disable the trigger by setting the value to 0.

Example:
    trigger = TriggerController(board)

    trig_vals = [1000, 0, 1000, 0]
    trigger.trigger_values = trig_vals

    trigger.write_triggers()

AUTHOR:
Marcus Luck <marcus@naluscientific.com>

"""
import logging
from typing import List

from naludaq.communication import AnalogRegisters, ControlRegisters, DigitalRegisters
from naludaq.controllers.controller import Controller

LOGGER = logging.getLogger(__name__)  # pylint ignore=invalid-name


class TriggerController(Controller):
    """Primary tool to setup the triggers for an aquisition.

    Attributes:
        board: The board to update the triggers on.
        trigger_offsets: Offsets as a list, one val per channel.
        trigger_values: The trigger values as a list, one val per channel.
        baseband_attempts: Times to run threshold scan to establish trigger baseband.

    Functions:
        write_triggers: writes all the trigger values to the physical hardware.
    """

    def __init__(self, board):
        super(TriggerController, self).__init__(board)
        # self.board = board
        self._wait = board.params["wait"]
        self._wbias = board.params["wbias"]
        self._num_trig_chans = board.params["channels"]
        self.baseband_attempts = 2
        self.bank = 1

    @property
    def trigger_offsets(self):
        """Set voltage offset for the trigger.

        Set the trigger offset values, can set one value for all channels or
        a specific value for each channel.

        Updates the value on the hardware if connected.

        Args:
            offset(int): voltage offset for all channels.
            offset(list): voltage offset for the individual channels.

        Returns:
            List of current voltage offsets.

        Raises:
            TypeError if voltage is not a list of length num_chans or a single number.
        """
        return self.board.trigger_offsets

    @trigger_offsets.setter
    def trigger_offsets(self, offset) -> None:
        if isinstance(offset, (int, float)):
            self.board.trigger_offsets = [offset] * self._num_trig_chans

        elif isinstance(offset, list) and len(offset) == self._num_trig_chans:
            self.board.trigger_offsets = offset

        else:
            raise TypeError("Voltage offset must be a single number or a list.")

        self.write_triggers()

    @property
    def trigger_values(self) -> List[int]:
        """Trigger threshold for the board.

        Set the trigger threshold values, can set one value for all channels or
        a specific value for each channel.

        Updates the value on the hardware if connected.

        Args:
            trigger_val (list or int): Threshold values for triggers per channel.
                Can take an single number for all channels or one value per channel.

        Returns:
            List of current values for the triggers.

        Raises:
            TypeError if not a List[int].
            ValueError if the list is the wrong length
        """
        return self.board.trigger_values

    @trigger_values.setter
    def trigger_values(self, trigger_val: List[int]) -> None:
        if isinstance(trigger_val, int):
            trigger_val = [trigger_val for _ in range(self._num_trig_chans)]
        try:
            self.board.trigger_values = trigger_val
        except:
            raise
        self.write_triggers()

    def write_triggers(self):
        """Write the trigger values to the hardware.

        This writes the current set triggers to the hardware.
        By setting the trigger_offsets or the trigger_values
        this function is called automatically and the hardware is updated.
        """
        self._set_trigger_thresholds()
        self._set_wbiases()
        self._set_trigger_offsets()

        return True

    def _set_trigger_thresholds(self):
        """Sets the trigger values and send to hardware.

        Take the trigger values from the board
        """
        trigger_values = self.board.trigger_values
        channels = self.board.params["channels"]

        reg = "trigger_threshold_{:02}"
        if self.board.params["model"] == "siread":
            reg = "thresh_{:02}"

        for chan in range(channels):
            register = reg.format(chan)
            tval = trigger_values[chan]
            self._write_analog_register(register, tval)

    def _set_wbiases(self):
        channels = self.board.params["channels"]
        wbias = [0] * (channels // self.bank)
        for index in range(channels // self.bank):
            if any(
                x > 0
                for x in self.board.trigger_values[
                    index * self.bank : index * self.bank + self.bank
                ]
            ):
                wbias[index] = self._wbias

            register = "wbias_" + str(index).zfill(2)
            self._write_analog_register(register, wbias[index])

    def _set_trigger_offsets(self):

        vofs = self.board.trigger_offsets

        channels = self.board.params["channels"]
        # if self.board.params['analog_values'].get('offset_00', None) is not None:
        areg = self.board.registers.get("analog_registers", {})
        if areg.get("offset_00", None) is not None:
            for index in range(channels // self.bank):
                register = "offset_" + str(index).zfill(2)
                self._write_analog_register(register, int(vofs[index]))

    def set_trigger_edge(self, raising: bool = True):
        """Set which signal edge to trigger on.

        Shift between positive going signals (raising) and negative (falling).

        Args:
            raising(bool): If true, trigger on positive going signals, else falling edge.

        Raises:
            TypeError if raises is not a bool.
        """
        if not isinstance(raising, bool):
            raise TypeError("raising must be a bool, got %s", type(raising))

        self._write_analog_register("sgn", raising)

    def _write_analog_register(self, register, value, chips: "int | list[int]" = None):
        """wrapper for the Analog register coms module.

        Args:
            register (str): name of the register to update.
            value: The register value to set.

        """
        AnalogRegisters(self.board, chips).write(register, value)

    def _write_control_register(self, register, value):
        """wrapper for the Control register coms module.

        Args:
            register (str): name of the register to update.
            value: The register value to set.

        """
        ControlRegisters(self.board).write(register, value)

    def _write_digital_register(self, register, value, chips: "int | list[int]" = None):
        """wrapper for the Digital register coms module.

        Args:
            register (str): name of the register to update.
            value: The register value to set.

        """
        DigitalRegisters(self.board, chips).write(register, value)
