import logging
import pathlib
from typing import Optional
from logging.handlers import RotatingFileHandler


def default_logger(name=__name__, level=logging.INFO):
    """创建一个默认的logger

    :param name: logger的名称, 默认为调用模块的名称
    :param level: 日志级别, 默认为DEBUG
    :return: 配置好的logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


def file_logger(fp: pathlib.Path, level=logging.DEBUG, name=None) -> logging.Logger:
    """
    创建并返回一个配置好的 Logger, 它会将日志信息输出到指定的文件路径。

    :param fp: 一个 pathlib.Path 对象，指定日志文件的路径。
    :param level: 日志级别, 默认为DEBUG。
    :param name: logger的名称, 默认为文件路径转换的字符串。
    :return: 配置好的 logging.Logger 对象。
    """
    if name is None:
        name = str(fp)
    fp.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not any(isinstance(handler, RotatingFileHandler) and handler.baseFilename == str(fp.absolute()) for handler in logger.handlers):
        file_handler = RotatingFileHandler(str(fp), maxBytes=10**6, backupCount=5)
        file_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.propagate = False

    return logger


class WithLogger:
    """With Logger Mixin"""
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """
        Args:
            logger (Optional[logging.Logger], optional): logger. Defaults to None.
        """
        self.logger = logger if logger else default_logger(__name__)
    

__all__ = [
    "file_logger",
    "default_logger",
    "WithLogger",
]