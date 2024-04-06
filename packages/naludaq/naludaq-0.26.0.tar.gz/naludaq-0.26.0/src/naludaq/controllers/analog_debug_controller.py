"""
WIP module for working with AODS or other boards through analog debug mode

Kenneth Lauritzen
"""
import time

from naludaq.communication import ControlRegisters
from naludaq.controllers.controller import Controller


class AnalogDebugController(Controller):
    def analog_debug_enable(self):
        """Sets up the control registers to allow for analog debug."""

        ControlRegisters(self.board).write_register_from_name("iomode0", 0)
        ControlRegisters(self.board).write_register_from_name("nrw", 1)
        ControlRegisters(self.board).write_register_from_name("addr_user", True)
        ControlRegisters(self.board).write_register_from_name("data_user", True)

        ControlRegisters(self.board).write_register_from_name("regclr", 1)
        time.sleep(0.5)
        ControlRegisters(self.board).write_register_from_name("regclr", 0)
        return True

    def analog_debug_disable(self):

        ControlRegisters(self.board).write_register_from_name("iomode0", 1)
        ControlRegisters(self.board).write_register_from_name("nrw", 0)
        ControlRegisters(self.board).write_register_from_name("addr_user", False)
        ControlRegisters(self.board).write_register_from_name("data_user", False)

    def direct_register_write(self, addr, data):

        pclk_registers = range(11)
        ControlRegisters(self.board).write_register_from_name("addr", addr)
        ControlRegisters(self.board).write_register_from_name("data", data)

        if addr in pclk_registers:
            ControlRegisters(self.board).write_register_from_name("sel", 1)
            time.sleep(0.5)
            ControlRegisters(self.board).write_register_from_name("sel", 0)
        else:
            ControlRegisters(self.board).write_register_from_name("pclk", 1)
            time.sleep(0.5)
            ControlRegisters(self.board).write_register_from_name("pclk", 0)
