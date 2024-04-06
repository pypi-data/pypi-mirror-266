"""

"""
import logging
import time

import numpy as np

from naludaq.communication.analog_registers import AnalogRegisters
from naludaq.controllers import get_readout_controller, get_trigger_controller
from naludaq.helpers import type_name
from naludaq.tools.threshold_scan.threshold_scan import ThresholdScan

LOGGER = logging.getLogger("naludaq.threshold_scan")


class ThresholdScanHdsoc(ThresholdScan):
    """Tool for sweeping over trigger thresholds and counting number of triggers.
    Can be used to determine the ideal point to set the trigger.

    """

    def __init__(
        self,
        board,
        *args,
        low_ref_value: int = None,
        high_ref_value: int = None,
        **kwargs,
    ):
        """Threshold scan for hdsoc boards.

        Args:
            board (Board): board object
            start_value (int): the start value for the scan
            stop_value (int): the stop value for the scan
            step_size (int): the step size for the scan
            low_ref_value (int): low reference value
            high_ref_value (int): high reference value
        """
        super().__init__(board, *args, **kwargs)
        trigger_params = self.board.params.get("trigger", {})
        self._min_ref = trigger_params.get("min_ref", 0)
        self._max_ref = trigger_params.get("max_ref", 15)
        self.low_ref_value = low_ref_value
        self.high_ref_value = high_ref_value

    @property
    def low_ref_value(self) -> int:
        """Get/set the low trigger reference value used during the scan"""
        return self._low_ref_value

    @low_ref_value.setter
    def low_ref_value(self, value: int):
        if value is None:
            value = self.board.params.get("threshold_scan", {}).get("low_ref", 0)
        if not isinstance(value, int):
            raise TypeError(f"Value must be int, not {type_name(value)}")
        if not self._min_ref <= value <= self._max_ref:
            raise ValueError(
                f"Value {value} is out of bounds for range "
                f"{self._min_ref} - {self._max_ref}"
            )
        self._low_ref_value = value

    @property
    def high_ref_value(self) -> int:
        """Get/set the high trigger reference value used during the scan"""
        return self._high_ref_value

    @high_ref_value.setter
    def high_ref_value(self, value: int):
        if value is None:
            value = self.board.params.get("threshold_scan", {}).get("high_ref", 0)
        if not isinstance(value, int):
            raise TypeError(f"Value must be int, not {type_name(value)}")
        if not self._min_ref <= value <= self._max_ref:
            raise ValueError(
                f"Value {value} is out of bounds for range "
                f"{self._min_ref} - {self._max_ref}"
            )
        self._high_ref_value = value

    def run(self, pause: float = 0.1):
        """Reimplementation to perform extra validation"""
        self._validate_scan_settings_or_raise()
        return super().run(pause)

    def _get_scalar_values(self, pause: float = 0.1):
        """Reimplementation to perform some extra setup."""
        self._set_tsel_enabled(left=True, right=True)
        rc = get_readout_controller(self.board)
        tc = get_trigger_controller(self.board)
        rc.set_readout_channels(self.channels)
        for side in ["left", "right"]:
            tc.update_reference_voltages(side, self.low_ref_value, self.high_ref_value)
        return self._get_scalar_values_vertical(pause)

    def _backup_board_settings(self):
        """Back up the trigger values, readout channels, references, and tsel"""
        super()._backup_board_settings()
        rc = get_readout_controller(self.board)
        tc = get_trigger_controller(self.board)
        self._original_readout_channels = rc.get_readout_channels()
        self._original_left_references = tc.left_references
        self._original_right_references = tc.right_references
        self._original_left_tsel = self._get_analog_register("tsel_left")
        self._original_right_tsel = self._get_analog_register("tsel_right")

    def _restore_board_settings(self):
        """Restore the trigger values, readout channels, references, and tsel"""
        super()._restore_board_settings()
        rc = get_readout_controller(self.board)
        tc = get_trigger_controller(self.board)
        rc.set_readout_channels(self._original_readout_channels)
        tc.update_reference_voltages("left", *self._original_left_references)
        tc.update_reference_voltages("right", *self._original_right_references)
        self._set_tsel_enabled(self._original_left_tsel, self._original_right_tsel)

    def _set_tsel_enabled(self, left: bool, right: bool):
        """Set whether tsel is enabled on each side.

        During the threshold scan, tsel must be enabled for scalars
        to read correctly.
        """
        AnalogRegisters(self.board).write("tsel_left", left)
        AnalogRegisters(self.board).write("tsel_right", right)

    def _get_analog_register(self, register: str) -> int:
        """Get the value of an analog register"""
        return self.board.registers["analog_registers"][register]["value"][0]

    def _validate_scan_settings_or_raise(self):
        """Raise an error if scan settings don't make sense"""
        if self.low_ref_value >= self.high_ref_value:
            raise ValueError("Low reference cannot exceed the high reference")

    def _get_scalar_values_vertical(self, pause: float) -> np.ndarray:
        """Scan the range and return np.array with trigger amounts

        Args:
            pause (float): amount of seconds to pause in between samples.

        Returns:
            Triggers value per channel as `np.array`.
        """
        scan_values = self.scan_values
        output = np.zeros((self.board.channels, len(scan_values)))

        # NOTE: the default threshold scan iterates over scan values then channels,
        # but on HDSoC it is super important that this order is reversed!
        # Otherwise the threshold scan will be super messed up or not work at all.
        for ch_i, chan in enumerate(self.channels):
            for i, value in enumerate(scan_values):
                if self._cancel:
                    break
                progress = ch_i * len(scan_values) + i + 1
                progress_total = len(self.channels) * len(scan_values)
                LOGGER.debug("Scan progress: %s/%s", progress, progress_total)
                self._progress.append(
                    (
                        int(95 * progress / progress_total),
                        f"Scanning {progress}/{progress_total}",
                    )
                )
                trigger_values = [1 for _ in range(self.board.channels)]
                trigger_values[chan] = int(value)
                self._trigger_controller.trigger_values = trigger_values  # int(value)
                time.sleep(pause)

                scalar = self._get_single_scalar_value(chan)
                output[chan][i] = scalar

        return output

    def _get_single_scalar_value(self, channel) -> list[int]:
        """Gets a reading from all scalers on the board.

        Returns:
            list[int]: scalar values ordered by channel.
        """
        return self._board_controller.read_scalar(channel)
