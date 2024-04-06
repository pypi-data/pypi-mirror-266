from .asoc import ASoCHeaderParser
from .asocv2 import ASoCv2HeaderParser
from .base import NoOpHeaderParser
from .siread import SiREADHeaderParser
from .trbhm import TrbhmHeaderParser
from .upac32 import UPAC32HeaderParser

_HEADER_PARSERS = {
    "aardvarcv2": ASoCHeaderParser(),
    "aardvarcv3": ASoCHeaderParser(),
    "aodsv1": ASoCv2HeaderParser(),
    "aodsv2_eval": ASoCv2HeaderParser(),
    "asoc": ASoCHeaderParser(),
    "asocv2": ASoCv2HeaderParser(),
    "asocv3": ASoCv2HeaderParser(),
    "hdsocv1": ASoCHeaderParser(),
    "hdsocv1_evalr1": ASoCHeaderParser(),
    "hdsocv1_evalr2": ASoCHeaderParser(),
    "hiper": ASoCHeaderParser(),
    "siread": SiREADHeaderParser(),
    "trbhm": TrbhmHeaderParser(),
    "udc16": NoOpHeaderParser(),
    "upac32": UPAC32HeaderParser(),
    "upaci": UPAC32HeaderParser(),
    "zdigitizer": UPAC32HeaderParser(),
    "default": NoOpHeaderParser(),
}


def get_header_parser(model: str):
    """Gets a header parser function appropriate for the given board.

    Args:
        model (str): the board model

    Returns:
        The header parser function.
    """
    return _HEADER_PARSERS.get(model, NoOpHeaderParser()).parse_header
