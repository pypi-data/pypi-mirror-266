"""Trigger controller for the HDSoC series of eval boards.

The HDSoC trigger circuit operates differently than the typical way
found on other boards. The HDSoC allows the reference voltages to be
set arbitrarily, theoretically giving the user a higher level of
control and precision over where the trigger threshold is set.

That being said, the trigger circuit is also highly non-linear,
making it difficult to set manually.
"""
import logging

import numpy as np

from naludaq.helpers.helper_functions import type_name

from .default import TriggerController

logger = logging.getLogger("naludaq.trigger_controller_hdsoc")


class TriggerControllerHdsoc(TriggerController):
    """Trigger controller for the HDSoC board

    HDSoC has a different division of the Trigger circuit.
    The trigger is set with an 8-bit value but the upper and lower
    reference voltages for the trigger circuit can be set.
    The upper and lower reference voltages are set for 0-15 and 16-31
    """

    def __init__(self, board):
        super().__init__(board)
        self._max_reference_value = (
            2 ** board.params.get("trigger", {}).get("ref_bits", 4) - 1
        )
        self._max_threshold_value = (
            2 ** board.params.get("trigger", {}).get("val_bits", 8) - 1
        )
        self._trig_thresh_regname = "trigger_threshold_{}"
        self._first_right_channel = 16

    @property
    def max_reference_value(self) -> int:
        """Maximum trigger reference value"""
        return self._max_reference_value

    @property
    def max_threshold_value(self) -> int:
        """Maximum trigger value"""
        return self._max_threshold_value

    @property
    def left_references(self) -> tuple[int, int]:
        """Get the current low/high references for the left side"""
        return (
            self._get_analog_register(f"sub_ref_neg_sb_left_trigger"),
            self._get_analog_register(f"sub_ref_pos_sb_left_trigger"),
        )

    @property
    def right_references(self) -> tuple[int, int]:
        """Get the current low/high references for the right side"""
        return (
            self._get_analog_register(f"sub_ref_neg_sb_right_trigger"),
            self._get_analog_register(f"sub_ref_pos_sb_right_trigger"),
        )

    def update_reference_voltages(self, side: str, lower: int, upper: int):
        """Update the reference voltage subrange for one side of the trigger circuit.

        Sets the VSS/VDD reference voltages in order to gain higher precision
        of the trigger thresholds around a region of interest.

        Args:
            side (str): the side of the trigger circuit; left or right.
            lower (int): the lower boundary of the subrange in counts.
            upper (int): the upper boundary of the subrange in counts.
        """
        side = side.lower()
        self._validate_reference_range_or_raise(side, lower, upper)
        logger.debug(
            "Updating references voltages for %s side: lower=%s, upper=%s",
            side,
            lower,
            upper,
        )
        self._write_analog_register(f"sub_ref_neg_sb_{side}_trigger", lower)
        self._write_analog_register(f"sub_ref_pos_sb_{side}_trigger", upper)

    def set_trigger_edge(self, side: str, rising: bool = True):
        """Set which signal edge to trigger on.

        Shift between positive going signals (raising) and negative (falling).

        Args:
            rising(bool): If true, trigger on positive going signals, else falling edge.

        Raises:
            TypeError if raises is not a bool.
        """
        self._validate_side_or_raise(side)
        if rising not in [True, False]:
            raise TypeError(f"rising must be a bool, got {rising}")
        logger.debug(
            "Setting %s trigger edge to: %s", side, "rising" if rising else "falling"
        )
        register = {
            "left": "tsgn_left",
            "right": "tsgn_right",
        }[side]
        self._write_analog_register(register, not rising)

    def _set_trigger_thresholds(self):
        """Set the trigger values for the individual channels using the values
        stored in the board object.
        """
        trigger_values = self.trigger_values
        self._validate_trigger_thresholds_or_raise(trigger_values)
        self._set_tsel_enabled()
        logger.debug(
            "Setting trigger thresholds: %s",
            {c: t for c, t in enumerate(trigger_values)},
        )
        for channel, threshold_value in enumerate(trigger_values):
            register_name = self._trig_thresh_regname.format(channel)
            self._write_analog_register(register_name, threshold_value)

    def _set_wbiases(self):
        """Enable the biasing system if it's not already enabled"""
        # power the dacs which set Vdd and Vss
        self._write_analog_register("ref_output_bias_left", 0x3E8)
        self._write_analog_register("ref_output_bias_bias_left", 0x3E8)

        self._write_analog_register("ref_output_bias_right", 0x3E8)
        self._write_analog_register("ref_output_bias_bias_right", 0x3E8)

        self._write_analog_register("channel_wbias_source_left", 0x400)
        self._write_analog_register("channel_wbias_source_right", 0x400)

    def _set_tsel_enabled(self):
        """Set whether tsel_{l/r} is enabled based on the trigger values.

        A side is enabled if at least one trigger value is non-zero for that side.
        """
        trigger_values = self.trigger_values
        split_pos = self._first_right_channel
        en_left = any(t != 0 for t in trigger_values[:split_pos])
        en_right = any(t != 0 for t in trigger_values[split_pos:])
        logger.debug("Setting tsel_left: %s", en_left)
        self._write_analog_register("tsel_left", en_left)
        logger.debug("Setting tsel_right: %s", en_right)
        self._write_analog_register("tsel_right", en_right)

    def _set_trigger_offsets(self):
        """Trigger offsets not implemented yet."""
        pass

    def _validate_trigger_thresholds_or_raise(self, trigger_values: list[int]):
        """Validate the trigger values are within the range of the trigger circuit."""
        max_threshold_value = self.max_threshold_value
        if not isinstance(trigger_values, (list, np.ndarray)):
            raise TypeError(
                f"Trigger values must be list, not {type_name(trigger_values)}"
            )
        if any(not isinstance(x, int) for x in trigger_values):
            raise TypeError("Trigger values must all be int")
        if any(not 0 <= x <= max_threshold_value for x in trigger_values):
            raise ValueError(
                f"Trigger value must be between 0 and {max_threshold_value}"
            )

    def _validate_side_or_raise(self, side: str):
        VALID_SIDES = ["left", "right"]
        if not isinstance(side, str):
            raise TypeError(f"Side must be str, not {type_name(side)}")
        if side not in VALID_SIDES:
            raise ValueError(f"Side must be one of: {VALID_SIDES}. Got: {side}")

    def _validate_reference_range_or_raise(self, side: str, lower: int, upper: int):
        """Validate reference range arguments.

        Args:
            side (str): must be "left" or "right"
            lower (int): must be within bounds
            upper (int): must be within bounds
        """
        self._validate_side_or_raise(side)
        for x in (lower, upper):
            if not isinstance(x, int):
                raise TypeError(
                    f"Reference boundary must be int, not {type_name(side)}"
                )
            if not 0 <= x <= self.max_reference_value:
                raise ValueError(
                    f"Reference boundary is out of bounds (0-{self.max_reference_value}). Got: {x}"
                )

    def _validate_reference_dict_or_raise(self, values: dict):
        """Validate reference dict or raise an error.

        The dict must have the form:
        ```
        {
            'left': [lower, upper],
            'right': [lower, upper],
        }
        ```
        """
        if not isinstance(values, dict):
            raise TypeError(f"Reference values must be a dict, not {type_name(values)}")
        if any(not isinstance(x, (list, tuple)) for x in values.values()):
            raise TypeError("Reference value ranges must be list or tuple")
        if any(len(x) != 2 for x in values.values()):
            raise ValueError(
                "Reference value ranges must each be length 2 (lower & upper)"
            )
        for side, (lower, upper) in values.items():
            self._validate_reference_range_or_raise(side, lower, upper)

    def _get_analog_register(self, register: str) -> int:
        """Get the value of an analog register"""
        return self.board.registers["analog_registers"][register]["value"][0]
