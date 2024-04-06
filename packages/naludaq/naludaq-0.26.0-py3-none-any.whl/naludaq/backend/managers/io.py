from naludaq.backend.managers.base import Manager


class BoardIoManager(Manager):
    def __init__(self, board):
        """Utility for I/O with a board connected to the backend.

        Args:
            context (Context): context used to communicate with the backend.
        """
        super().__init__(board)

    def write(self, command: "str | bytes | list[str | bytes]"):
        """Writes a non-read command to the board.

        Args:
            command (str | bytes): command to send.
        """
        self.write_all([command])

    def write_all(self, commands: "list[str | bytes]"):
        """Writes a list of non-read commands to the board.

        Args:
            commands (list[str | bytes]): the commands to send.
        """
        if len(commands) == 0:
            raise ValueError("Need at least one command")
        commands = [c.hex() if isinstance(c, bytes) else c for c in commands]
        self.context.client.put(
            "/board/raw",
            json={"packages": commands},
        )

    def read(self, command: "str | bytes") -> bytes:
        """Sends a read command to the board and gets the response.

        Args:
            command (str | bytes): read command to send.

        Returns:
            bytes: the response.
        """
        return self.read_all([command])[0]

    def read_all(self, commands: "list[str | bytes]") -> list[bytes]:
        """Sends several read commands to the board and retrieves the responses.

        Args:
            commands (list[str | bytes]): commands to send

        Returns:
            list[bytes]: The responses from the board
        """
        if len(commands) == 0:
            raise ValueError("Need at least one command")
        commands = [c.hex() if isinstance(c, bytes) else c for c in commands]
        response = self.context.client.get_json(
            "/board/raw",
            json={"packages": commands},
        )

        return [bytes.fromhex(a) for a in response["packages"]]
