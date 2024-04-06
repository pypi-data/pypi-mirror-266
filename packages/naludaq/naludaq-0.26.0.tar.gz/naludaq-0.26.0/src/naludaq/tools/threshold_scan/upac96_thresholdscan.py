import time
from typing import Dict

import numpy as np

from naludaq.communication import ControlRegisters
from naludaq.controllers.trigger import get_trigger_controller
from naludaq.tools.threshold_scan.threshold_scan import ThresholdScan


class Upac96ThresholdScan(ThresholdScan):
    """Scan each trigger value and read the scaler values for each channel."""

    def _get_scalar_values(self, pause: float) -> np.ndarray:
        """Scan the range and return np.array with trigger amounts.

        Args:
            pause (float): amount of seconds to pause in between samples.

        Returns:
            Triggers value per channel as `np.array`.
        """
        trigger_select_backup = self._get_ctrl_reg("trigger_select")
        self._set_ctrl_reg("trigger_select", 1)
        scan_values = self.scan_values
        output = np.zeros((self.board.channels, len(scan_values)))

        try:
            bundle_bk = self.board.connection.bundle_mode
            bk_tx_pause = self.board.connection.tx_pause
            self.board.connection.bundle_mode = True
            self.board.connection.tx_pause = 0
        except AttributeError:
            bundle_bk = None
            bk_tx_pause = None
        for i, value in enumerate(scan_values):
            if self._cancel:
                break
            self._progress.append(
                (int(95 * i / len(scan_values)), f"Scanning {(i+1)}/{len(scan_values)}")
            )
            time.sleep(pause)

            scals = self._get_scaler_value(value)

            for chan in self.channels:
                output[chan][i] = scals[chan]
        self._set_ctrl_reg("trigger_select", trigger_select_backup)

        if bundle_bk is not None and bk_tx_pause is not None:
            self.board.connection.bundle_mode = bundle_bk
            self.board.connection.tx_pause = bk_tx_pause

        return output

    def _get_scaler_value(self, trigger_value) -> Dict[int, int]:
        """Read the scalers for selected channels for a specific trigger value.

        Args:
            channels (list): list of channels to scan the scalers

        Returns:
            dict of scaler values for the selected channels
        """
        scalers = {}
        for chan in self.channels:
            scal = self._read_scaler(chan, trigger_value)
            scalers[chan] = scal

        return scalers

    def _read_scaler(self, channel, trigger_value):
        """Read the scaler value for a specific channel and trigger value.

        Args:
            channel (int): channel to read the scaler from
            trigger_value (int): trigger value to scan

        Returns:
            Scaler value for the channel
        """
        trigger_vals = [0 for _ in range(self.board.channels)]
        trigger_vals[channel] = int(trigger_value)
        tc = get_trigger_controller(self.board)
        tc.trigger_values = trigger_vals
        self._reset_counter()
        scal = self._get_scalar()
        return scal

    def _get_scalar(self) -> int:
        """Read and combine the scalar values from the two 16-bit registers."""
        upper = self._get_ctrl_reg("count_msb")
        lower = self._get_ctrl_reg("count_lsb")
        scaler = (upper << 16) + lower
        return scaler

    def _get_ctrl_reg(self, name: str):
        return ControlRegisters(self.board).read(name)["value"]

    def _set_ctrl_reg(self, name: str, value: int):
        ControlRegisters(self.board).write(name, value)

    def _reset_counter(self):
        """Reset the counter to 0."""
        self._set_ctrl_reg("count_reset", 1)
        self._set_ctrl_reg("count_reset", 0)
