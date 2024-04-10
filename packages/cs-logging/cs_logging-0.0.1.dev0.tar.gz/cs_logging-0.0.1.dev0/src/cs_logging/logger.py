# Based on:
# https://github.com/tenstorrent/tt-buda/blob/2f4a8ee76cb134c293029fccf478d9acf97e5428/utils/logger.hpp
import logging


class TerminalColor:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    ORANGE = "\033[38;5;208m"

    @staticmethod
    def custom_color(r, g, b, bold=True):
        bold_code = "1;" if bold else ""
        ANSI_ESCAPE = f"\033[{bold_code}38;2;{r};{g};{b}m"
        return ANSI_ESCAPE

    # Define custom RGB colors with bold
    RED = custom_color(255, 0, 0)
    GREEN = "\033[1;32m"  # Bold standard green
    YELLOW = custom_color(255, 255, 0)
    BLUE = "\033[1;38;5;111m"  # Bold cornflower blue
    ORANGE = custom_color(255, 165, 0)
    PURPLE = "\033[1;38;5;55m"  # Bold 256-color purple
    CYAN = "\033[1;36m"
    WHITE = custom_color(255, 255, 255)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": TerminalColor.PURPLE,
        "INFO": TerminalColor.BLUE,
        "WARNING": TerminalColor.YELLOW,
        "ERROR": TerminalColor.ORANGE,
        "CRITICAL": TerminalColor.RED,
    }

    def __init__(self, fmt, module_to_watch=None):
        super().__init__(fmt)
        self.module_to_watch = module_to_watch if module_to_watch else None
        self.levelname_length = max(len(level) for level in self.COLORS)

    def format(self, record):
        levelname = record.levelname
        padded_levelname = levelname.ljust(self.levelname_length)

        # Change color for INFO level based on the module
        if levelname == "INFO" and record.module == self.module_to_watch:
            info_color = TerminalColor.RED  # Define this special color
        else:
            info_color = self.COLORS[levelname]

        log_fmt = f"{TerminalColor.GREEN}%(asctime)s{TerminalColor.RESET} | "
        log_fmt += f"{info_color}{padded_levelname}{TerminalColor.RESET} | "
        log_fmt += f"{TerminalColor.CYAN}%(module)s.%(funcName)s:%(lineno)d{TerminalColor.RESET} - "
        message_color = (
            TerminalColor.PURPLE
            if record.levelno == logging.DEBUG
            else TerminalColor.WHITE
        )
        log_fmt += f"{message_color}%(message)s{TerminalColor.RESET}"
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S.%f")
        self._style._fmt = log_fmt
        return super().format(record)


class LoggerConfig:
    def __init__(self, module_to_watch=None):
        handler = logging.StreamHandler()
        handler.setFormatter(
            ColoredFormatter("%(message)s", module_to_watch=module_to_watch)
        )
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)

    def get_logger(self, name):
        return logging.getLogger(name)


# Usage example:
logger_config = LoggerConfig()
logger = logger_config.get_logger(__name__)


def s1():
    logger.info("This is an info message")
