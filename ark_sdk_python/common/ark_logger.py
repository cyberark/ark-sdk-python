import logging
import os
import sys
from typing import Final, Optional

LOGGER_STYLE: Final[str] = 'LOGGER_STYLE'
LOG_LEVEL: Final[str] = 'LOG_LEVEL'

LOGGER_STYLE_DEFAULT: Final[str] = 'default'


class ArkLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.CRITICAL, verbose=True):
        super().__init__(name, level)
        self.__verbose = verbose

    @property
    def verbose(self) -> bool:
        return self.__verbose

    @verbose.setter
    def verbose(self, value: bool):
        self.__verbose = value

    def notice(self, msg, *args, **kwargs):
        from colorama import Fore, Style

        if not self.__verbose:
            return
        color_msg = f"{Fore.GREEN}{Style.BRIGHT}" f"{msg}{Style.RESET_ALL}{Fore.RESET}"
        return super().info(f"{color_msg}", *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        from colorama import Fore

        if not self.__verbose:
            return
        color_msg = f"{Fore.GREEN}" f"{msg}{Fore.RESET}"
        return super().info(f"{color_msg}", *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        from colorama import Fore

        if not self.__verbose:
            return
        color_msg = f"{Fore.YELLOW}" f"{msg}{Fore.RESET}"
        return super().warning(f"{color_msg}", *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        from colorama import Fore

        if not self.__verbose:
            return
        color_msg = f"{Fore.RED}" f"{msg}{Fore.RESET}"
        return super().error(f"{color_msg}", *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        from colorama import Fore, Style

        if not self.__verbose:
            return
        color_msg = f"{Fore.RED}{Style.BRIGHT}" f"{msg}{Style.RESET_ALL}{Fore.RESET}"
        super().fatal(f"{color_msg}", *args, **kwargs)
        sys.exit(-1)


def get_logger(app: Optional[str] = None, log_level: Optional[int] = None):
    if not log_level:
        log_level = logging.getLevelName(os.getenv(LOG_LEVEL, 'CRITICAL'))
    logger_style = os.getenv(LOGGER_STYLE, 'default')
    if logger_style == 'default':
        log_format = '%(levelname)-8s | %(asctime)s | %(message)s'
        logging.setLoggerClass(ArkLogger)
        logging.basicConfig(format=format(log_format), datefmt="%H:%M:%S %d/%m/%Y", level=log_level)
        logger = logging.getLogger(app)
        logger.setLevel(log_level)
        return logger
