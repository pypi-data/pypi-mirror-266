import logging
from sys import stdout
from typing import Optional
from reclass.exceptions import (
    ReLogLevelUnknow
)
import reclass.constants as con


class ReLogger(logging.Logger):
    """ Reusable colored logger class.
        Initial version
    """
    DEFAULT_KWARGS = {
        "level": "warning",
        "format": "%(color_on)s%(levelname)s:%(name)s:%(message)s%(color_off)s"
    }

    def __init__(self, name: str,  **kwargs: Optional):
        super().__init__(name)
        kwargs = self.DEFAULT_KWARGS | kwargs
        self.log_level = kwargs.pop("level").upper()
        self.format = kwargs.pop("format")
        self.setLevel(logging.DEBUG)
        con_log = logging.StreamHandler(stdout)
        con_log.setLevel(self.log_level)
        con_formater = ReCollorFormater(enable_colors=True, fmt=self.format)
        con_log.setFormatter(con_formater)
        self.addHandler(con_log)

    def save_dabug_to_file(slef) -> None:
        pass

    def disable_colors(self) -> None:
        pass

    def enable_colors(self) -> None:
        pass


class ReCollorFormater(logging.Formatter):
    """ Class to add color_on and color_off
        parameters to logging formater
    """
    COLOR_CODES = {
        logging.DEBUG:    con.CYAN,
        logging.INFO:     con.GREEN,
        logging.CRITICAL: con.RED,
        logging.ERROR:    con.L_RED,
        logging.WARNING:  con.YELLOW,
    }
    RESET_CODE = con.DEFAULT_COLOR

    def __init__(self, enable_colors=False, *args, **kwargs):
        super(ReCollorFormater, self).__init__(*args, **kwargs)
        self.color = enable_colors

    def format(self, record, *args, **kwargs):
        if (self.color and record.levelno in self.COLOR_CODES):
            record.color_on = self.COLOR_CODES[record.levelno]
            record.color_off = self.RESET_CODE
        else:
            record.color_on = ""
            record.color_off = ""
        return super(ReCollorFormater, self).format(record, *args, **kwargs)
