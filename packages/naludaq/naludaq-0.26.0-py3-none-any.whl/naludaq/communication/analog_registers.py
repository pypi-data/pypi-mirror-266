"""Analog registers
===================
Registers controlling the analog part of the ASIC.

What are the analog registers?
It's a set of registers on the FPGA matching a set of registers on the chip
By changing these registers it controls the analog portion of the chip.

Command structure:
------------------
Updating the analog command uses a format 'BXMAAVVV'

- B tells the FPGA command parser to expect a analog/digital command.
- M is mode, 0 = write, 1 = read
- AA = address
- VVV = value

Will be interpereted by the FPGA as hex. it's 32-bit = 8 hex values.

Functions:
----------
- write_all
- write
- write2addr


"""
from logging import getLogger

from naludaq.communication._chip import ChipRegisters

LOGGER = getLogger(__name__)


class AnalogRegisters(ChipRegisters):
    def __init__(self, board, chips: "int | list[int]" = None):
        """Registers controlling the analog part of the ASIC(s).

        For a more thorough explanation of the multichip aspect and its implications,
        see the `multichip` module.

        Args:
            board (Board): board object
            chips (int | list[int] | None): chip(s) to write to. If None, all chips are assumed.
        """
        super().__init__(board, "analog_registers", chips)
        self._write_cmd = 0xB00
        self._width_cmd = 3
        self._width_addr = 2  # hex char
        self._width_val = 3  # hex char

    # READ #########################################################

    def _addr_value(self, addr: str, chip: int):
        """Reimplemented to correct strobe values."""
        if self.board.params.get("strobe_values_correction", False):
            result = self._correct_strobes(addr, chip)
        else:
            result = super()._addr_value(addr, chip)
        return result

    def _correct_strobes(self, addr: str, chip: int) -> int:
        """Generate the value from the hex address.

        An address can contain multiple registers.
        Generate the value depending on the bit positions of all registers on the address.

        Args:
            addr (str): Hex value of the address, 2 hex char long.

        Returns:
            int: value of the combined registers.

        Raises:
            AttributeError if the address is not valid.
        """
        addr = addr.upper()
        strobe_correction_keys = self.board.params.get("strobe_correction_keys", [])
        value = 0
        for name, register in self.registers_on_address(addr).items():
            reg_value = register["value"][chip]
            reg_pos = register["bitposition"]
            reg_width = register["bitwidth"]

            # FIX TIMING REGS, ACCORDING TO BOARD PARAMETER timing_correction
            if name in strobe_correction_keys:
                reg_value = self._fix_timing(reg_value)
            value += 2**reg_pos * (int(reg_value) % (2**reg_width))
        return value

    def _generate_write_atom(self, addr: str, value: int) -> str:
        """Generate the string to send to the board.

        OVERLOAD the standard way of generating the command since the analog command parsing
        sometimes

        Abstracts the model differences away from the main code, AARDVARCv2 got a timing hack.

        Args:
            board(obj)
            name(str): name of the analog register
            value(): Value to set the register to.
        """
        write_addr = f"{self._write_cmd:X}"
        cmd_addr = addr
        if len(addr) == 3:
            write_addr = f"B{addr[0]}0"
            cmd_addr = f"{addr[1:]}"
        if isinstance(value, (int, bool)):
            value = f"{value:X}".zfill(self._width_val)
        command = f"{write_addr}{cmd_addr}{value}"  # First 5 hex chars, address should be 3 hex. B001c
        return command

    @staticmethod
    def _fix_timing(in_value: int):
        """The timing signal data mux is all mixed up for simplicity of routing, so this fixes it

        Don't use unless you know what it does. Contains hardcoded values.
        """
        if in_value < 64:
            return in_value * 2 + 1
        return 254 - 2 * in_value
