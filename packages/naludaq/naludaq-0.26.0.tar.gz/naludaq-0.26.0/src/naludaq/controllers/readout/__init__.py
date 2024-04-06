from .aardvarcv3 import Aardvarcv3ReadoutController
from .asocv3 import Asocv3ReadoutController
from .default import ReadoutController
from .hdsoc import HDSoCReadoutController
from .trbhm import TrbhmReadoutController


def get_readout_controller(board):
    """Gets the readout controller which is appropriate for the given board.

    hdsocv1 -> HDSoCReadoutController
    aardvarcv3 => Aardvarcv3ReadoutController
    default -> ReadoutController

    Args:
        board (Board): the board object

    Returns:
        The readout controller.
    """
    return {
        "hdsocv1": HDSoCReadoutController,
        "hdsocv1_evalr1": HDSoCReadoutController,
        "hdsocv1_evalr2": HDSoCReadoutController,
        "aardvarcv3": Aardvarcv3ReadoutController,
        "aardvarcv4": Aardvarcv3ReadoutController,
        "asocv3": Asocv3ReadoutController,
        "asocv3s": Asocv3ReadoutController,
        "trbhm": TrbhmReadoutController,
        "aodsoc_aods": TrbhmReadoutController,
        "aodsoc_asoc": TrbhmReadoutController,
    }.get(board.model, ReadoutController)(board)
