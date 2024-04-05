import logging
from logging.handlers import TimedRotatingFileHandler

from tg_logger import BaseLogger


def get_logger(
        name: str = None,
        level: int = None,
        console_log_handler: logging.StreamHandler = None,
        file_log_handler: TimedRotatingFileHandler = None
) -> 'BaseLogger':
    """
    Configures a logger with optional console and file handlers.

    Parameters:
    - name (str, optional): The name of the logger.
    - level (int, optional): The log level.
    - console_log_handler (logging.StreamHandler, optional): A console log
        handler.
    - file_log_handler (TimedRotatingFileHandler, optional): A file log
        handler.

    Returns:
    - BaseLogger: The configured logger.
    """

    logger = logging.getLogger(name)
    if console_log_handler is not None:
        logger.addHandler(console_log_handler)
    if file_log_handler is not None:
        logger.addHandler(file_log_handler)
    if level is not None:
        logger.setLevel(level)
    return BaseLogger(logger=logger)
