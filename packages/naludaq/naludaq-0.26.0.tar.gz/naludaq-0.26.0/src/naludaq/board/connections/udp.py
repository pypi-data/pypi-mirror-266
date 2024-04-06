import binascii
import logging
import select
import socket
import time

import numpy as np

from naludaq.board.connections.base_connection import BaseConnection
from naludaq.parsers.answer_parser import get_answer_parser

logger = logging.getLogger(__name__)


class UDP(BaseConnection):
    def __init__(self, connection_info: dict):
        """Class for communication over an ethernet connection.

        Args:
            connection_info (dict): the connection configuration
        """
        super().__init__()

        # Store connection info
        user_ip = connection_info["user_ip"]
        board_ip = connection_info["board_ip"]
        command_port = connection_info["command_port"]
        readout_port = connection_info["readout_port"]
        self._user_command_addr = (user_ip, command_port)
        self._user_readout_addr = (user_ip, readout_port)
        self._board_command_addr = (board_ip, command_port)
        self._board_readout_addr = (board_ip, readout_port)

        self._model = connection_info["model"]
        self.stopword = connection_info["stop_word"]

        self.read_addr = "AD"
        self.write_addr = "AF"
        self.response_length = 8
        self.parse_answer = get_answer_parser(True)

        self.socket: socket.socket = None

    @property
    def user_command_addr(self) -> tuple:
        """Get/set the user command address.

        Setting the address will close and reopen the connection
        if the connection is already open

        Args:
            addr (tuple): the address
        """
        return self._user_command_addr

    @user_command_addr.setter
    def user_command_addr(self, addr: tuple):
        self._user_command_addr = addr

        # Reopen the socket
        if self.socket:
            self.close()
            self.open()

    @property
    def user_readout_addr(self) -> tuple:
        """Get/set the user readout address.

        Args:
            addr (tuple): the address
        """
        return self._user_readout_addr

    @user_readout_addr.setter
    def user_readout_addr(self, addr: tuple):
        self._user_readout_addr = addr

    @property
    def board_command_addr(self) -> tuple:
        """Get/set the board command address.

        Args:
            addr (tuple): the address
        """
        return self._board_command_addr

    @board_command_addr.setter
    def board_command_addr(self, addr: tuple):
        self._board_command_addr = addr

    @property
    def board_readout_addr(self) -> tuple:
        """Get/set the board readout address.

        Args:
            addr (tuple): the address
        """
        return self._board_readout_addr

    @board_readout_addr.setter
    def board_readout_addr(self, addr: tuple):
        self._board_readout_addr = addr

    @property
    def is_open(self) -> bool:
        """Indicates whether the connection is open."""
        return self.socket is not None

    def set_answer_parser(self, new_firmware: bool = True):
        """Sets the answer parser.

        Args:
            new_firmware (bool): whether to use the parser for new firmware
        """
        self.parse_answer = get_answer_parser(new_firmware)

    def reset_input_buffer(self):
        """Discards any data currently in the input buffer.

        Closes and re-opens the socket.
        """
        self.close()
        self.open()

    def reset_output_buffer(self):
        """Not implemented for ethernet connection."""
        pass

    def __del__(self):
        self.close()

    def open(self):
        """Opens the connection."""
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setblocking(False)
            self.socket.bind(self._user_command_addr)

    def close(self):
        """Closes the connection."""
        try:
            self.socket.close()
            self.socket = None
        except:
            pass

    def send(self, data: str, pause: float = 0.02):
        """Sends a string of hex characters.

        Args:
            data (str): the data string. Only hex characters are allowed!
            pause (float): the time in seconds to wait after sending
        """
        num_chars = len(data)

        # Make sure the length of the input is a multiple of 8
        if num_chars % 8 != 0:
            logger.debug(
                "UDP.send(): need multiples of 8 hex chars, you gave me %s", num_chars
            )
            logger.debug("command:%s", data)
            return

        # Convert hex data string to binary
        # data_binary = binascii.unhexlify(self.sync_word + data)
        data_binary = binascii.unhexlify(data)

        # Send the data over the socket
        self.socket.sendto(data_binary, self._board_command_addr)
        time.sleep(pause)

    @property
    def in_waiting(self) -> bool:
        """Checks data is waiting in the socket buffer."""
        data_in_socket, _, _ = select.select([self.socket], [], [], 0)
        return len(data_in_socket) != 0

    def receive(self, length: int = -1, timeout: int = 100, raw: bool = False):
        """Receives data from the socket.

        Args:
            length (int): the number of bytes to receive
            timeout (int): the number of milliseconds to wait before giving up
            raw (bool): return bytes (True), or return a hex string (False)

        Returns:
            Hex string or bytes, depending on the `raw` flag, or None if
            no data was received in time.
        """
        if length <= 0:
            length = self.response_length

        while not self.in_waiting and timeout > 0:
            timeout -= 1
            time.sleep(0.001)

        if not self.in_waiting:
            return None

        # Read a single command from the socket
        buff, _ = self.socket.recvfrom(length)

        if raw:
            return buff
        else:
            return binascii.hexlify(buff)

    def receive_all(self, timeout: int = 100, raw: bool = False):
        """Receives all waiting data from the socket.

        Args:
            timeout (int): the number of milliseconds to wait before giving up
            raw (bool): return bytes (True), or return a hex string (False)

        Returns:
            Hex string or bytes, depending on the `raw` flag, or None if
            no data was received in time.
        """
        return self.receive(length=self.in_waiting, timeout=timeout, raw=raw)

    def writeReg(self, regNum: int, value: int):
        """Sends a command to write a value to a register

        Args:
            regNum (int): the address of the register to write
            value (int): the value to write
        """
        command = self.write_addr + hex(regNum)[2:].zfill(2) + hex(value)[2:].zfill(4)
        self.send(command)

    def readReg(self, regNum: int, timeout: int = 1000) -> int:
        """Reads a register.

        Args:
            regNum (int): the address of the register to read from
            timeout (int): the number of milliseconds to wait before giving up

        Returns:
            The value held in the register, or None if an error occurred
        """
        cmd_id = self._send_readreg_cmd(regNum)

        # Read a single response from the socket
        while not self.in_waiting and timeout > 0:
            timeout -= 1
            time.sleep(0.001)

        if not self.in_waiting:
            logger.error("UDP.readReg(): Timed out, no data received")
            return None

        buff, _ = self.socket.recvfrom(self.response_length)
        buff = bytearray(buff)

        # Handle the data received
        answer = self.parse_answer(buff)
        if answer["cmd_id"] != cmd_id:
            logger.error(
                "UDP.readReg(): received command ID does not match the one sent"
            )
            return None

        return answer["value"]

    def _send_readreg_cmd(self, regNum) -> int:
        """Sends a command to read a register.

        Args:
            regNum (str, int): the register to read

        Returns:
            The command id used in the sent command
        """
        read_addr = int(self.read_addr, 16)
        if isinstance(regNum, str):
            regNum = int(regNum, 16)

        # Generate and send the command string (4 bytes)
        cmd_id = np.random.randint(0, 2**16)
        command = f"{read_addr:x}{regNum:02x}{cmd_id:04x}"

        self.send(command)

        return cmd_id
