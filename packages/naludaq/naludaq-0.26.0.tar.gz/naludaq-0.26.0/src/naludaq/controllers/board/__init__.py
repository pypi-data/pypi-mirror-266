"""Class containing all functions to control the boards.

All functions to communicate with the Nalu boards are
collected here. The Facade naludaq is intended to simplify
the interface for general use.
"""
import logging

from .aodsoc import BoardControllerAodsoc
from .asocv3s import ASoCv3SBoardController
from .default import BoardController
from .hdsoc import HDSoCBoardController
from .oleas import BoardControllerOleas
from .trbhm import TrbhmBoardController
from .udc import UDCBoardController
from .upac import UpacBoardController
from .upac96 import UPAC96BoardController

LOGGER = logging.getLogger(__name__)  # pylint: disable=invalid-name


def get_board_controller(board):
    """Get the correct board controller based on the board model.

    Args:
        board (Board): the board object.

    Returns:
        The appropriate BoardController for the given board.
    """
    return {
        # 'aodsoc_aods': BoardControllerAodsoc,
        "aodsoc_aods": BoardControllerOleas,
        "aodsoc_asoc": BoardControllerAodsoc,
        "hdsocv1": HDSoCBoardController,
        "hdsocv1_evalr1": HDSoCBoardController,
        "hdsocv1_evalr2": HDSoCBoardController,
        "asocv3s": ASoCv3SBoardController,
        "trbhm": TrbhmBoardController,
        "udc16": UDCBoardController,
        "upac32": UpacBoardController,
        "upaci": UpacBoardController,
        "upac96": UPAC96BoardController,
        "zdigitizer": UpacBoardController,
    }.get(board.model, BoardController)(board)
