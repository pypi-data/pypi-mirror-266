import logging
import time
from typing import Iterable

import numpy as np

from naludaq.controllers.board import get_board_controller
from naludaq.controllers.trigger import get_trigger_controller
from naludaq.helpers import type_name

LOGGER = logging.getLogger("naludaq.threshold_scan")


class ThresholdScan:
    """Tool for sweeping over trigger thresholds and counting number of triggers.
    Can be used to determine the ideal point to set the trigger.
    """

    def __init__(
        self,
        board,
        channels: Iterable[int] = None,
        scan_values: Iterable[int] = None,
    ):
        """Class to run ThresholdScan. Used to find the number of
        triggers for each trigger threshold.

        Args:
            board (Board): Board to run a threshold scan on
            threshold_values (Iterable[int]): threshold values to run the scan for.
        """
        self.board = board
        self.channels = channels
        self._cancel = False
        self._progress: list = []
        self._num_trig_chans = board.channels

        trigger_params = self.board.params.get("trigger", {})
        self._min_counts = trigger_params.get("min_counts", 0)
        self._max_counts = trigger_params.get("max_counts", 4095)
        self.scan_values = scan_values

        self._board_controller = get_board_controller(self.board)
        self._trigger_controller = get_trigger_controller(self.board)

    @property
    def trigger_values(self) -> list[int]:
        """Gets/sets board trigger values.
        Values must be a List[int]

        Raise:
            TypeError if not a list of ints.
            ValueError if number of trigger channels is incorrect for the board.
        """
        return self.board.trigger_values

    @trigger_values.setter
    def trigger_values(self, value: list[int]):
        self.board.trigger_values = value

    @property
    def channels(self) -> list[int]:
        """Get/set the channels to run the scan on."""
        return self._channels.copy()

    @channels.setter
    def channels(self, channels: Iterable[int]):
        if channels is None:
            channels = range(self.board.channels)
        if not isinstance(channels, Iterable):
            raise TypeError(
                f"Channels must be a Iterable[int], not {type_name(channels)}"
            )
        if any(not isinstance(c, int) for c in channels):
            raise TypeError("Channels must be a Iterable[int]")
        if any(not 0 <= c < self.board.channels for c in channels):
            raise ValueError("One or more channels is out of bounds")
        self._channels = list(channels)

    @property
    def scan_values(self) -> np.ndarray:
        """Gets/sets the threshold values to read the scalars for."""
        return self._threshold_values.copy()

    @scan_values.setter
    def scan_values(self, values: Iterable[int]):
        if values is None:
            values = self._default_scan_values()
        if not isinstance(values, Iterable):
            raise TypeError(f"Values must be a Iterable[int], not {type_name(values)}")
        values = np.array(values)
        if np.min(values) < self._min_counts or np.max(values) > self._max_counts:
            raise ValueError("One or more values is out of bounds")
        self._threshold_values = values

    def run(self, pause: float = 0.1):
        """Scan the scalars at the trigger values defined by the scan_values property.

        Returns the amount of hits for each scanned trigger value in the range.

        Args:
            pause (float): amount of seconds to pause in between samples.

        Returns:
            Tuple of (trigger value per channel as `np.array`, `irange` as list).
        """
        self._cancel = False
        self._progress.append((0, "Backing up board settings"))
        self._backup_board_settings()
        output = self._get_scalar_values(pause)
        self._progress.append((95, "Restoring board settings"))
        self._restore_board_settings()
        self._progress.append((100, "Done"))

        return (np.array(output), self.scan_values.copy())

    def _backup_board_settings(self):
        """Saves a copy of board trigger values to be restored later."""
        self._original_trigger_values = self.board.trigger_values.copy()

    def _restore_board_settings(self):
        """Restores the original trigger values from board."""
        self.trigger_values = self._original_trigger_values
        self._trigger_controller.write_triggers()

    def _get_scalar_values(self, pause: float) -> np.ndarray:
        """Scan the range and return np.array with trigger amounts

        Args:
            pause (float): amount of seconds to pause in between samples.

        Returns:
            Triggers value per channel as `np.array`.
        """
        scan_values = self.scan_values
        output = np.zeros((self.board.channels, len(scan_values)))
        for i, value in enumerate(scan_values):
            if self._cancel:
                break
            LOGGER.debug("Scan progress: %s/%s", i + 1, len(scan_values))
            self._progress.append(
                (int(95 * i / len(scan_values)), f"Scanning {(i+1)}/{len(scan_values)}")
            )
            self._trigger_controller.trigger_values = int(value)
            time.sleep(pause)

            scals = self._get_scaler_value()

            for chan in self.channels:
                output[chan][i] = scals[chan]
        return output

    def cancel(self):
        """Cancels the threshold scan if one is currently running.

        This function must be called from a different thread, as the
        threshold scan is blocking. The threshold scan will stop as
        soon as possible.
        """
        self._cancel = True

    def _get_scaler_value(self) -> list[int]:
        """Gets a reading from all scalers on the board.

        Returns:
            list[int]: scalar values ordered by channel.
        """
        return [x for x in self._board_controller.read_scalers(self.channels)]

    @property
    def progress(self):
        """Get/Set the progress message queue.

        This is a hook to read the progress if running threads.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError(
                "Progress updates are stored in an object with an 'append' method"
            )
        self._progress = value

    def _default_scan_values(self) -> np.ndarray:
        """Get the default scan values from the params"""
        scan_params = self.board.params.get("threshold_scan", {})
        return np.arange(
            scan_params.get("start", 500),
            scan_params.get("stop", 3500),
            scan_params.get("stepsize", 5),
        )
