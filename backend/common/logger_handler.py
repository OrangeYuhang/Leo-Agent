import logging
import os
from backend.common.path_tool import get_abs_path
from datetime import datetime

LOG_ROOT = get_abs_path('logs')
os.makedirs(LOG_ROOT, exist_ok=True)

DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

class ColoredFormatter(logging.Formatter):
    """按日志级别给整行着色（仅用于控制台）"""
    COLORS = {
        logging.DEBUG:    '\033[36m',  # 青色
        logging.INFO:     '\033[32m',  # 绿色
        logging.WARNING:  '\033[33m',  # 黄色
        logging.ERROR:    '\033[31m',  # 红色
        logging.CRITICAL: '\033[41m',  # 红底
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelno)
        msg = super().format(record)
        return f"{color}{msg}{self.RESET}" if color else msg

def get_logger(
    name: str,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    logfile = None
) -> logging.Logger:
    """_get a logger object_

    Args:
        name (str): _logger name_
        console_level (int, optional): _The level of console logger,_. Defaults to logging.INFO.
        file_level (int, optional): _The level of file logger_. Defaults to logging.DEBUG.
        logfile (_type_, optional): _The logfile path_. Defaults to None.

    Returns:
        logging.Logger: _description_
        
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    ))

    logger.addHandler(console_handler)

    if not logfile:
        logfile = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")

    file_handler = logging.FileHandler(logfile, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger


logger = get_logger('dev')

if __name__ == '__main__':
    logger.info('hello world')
    logger.warning('hello world')
    logger.error('hello world')
    logger.debug('hello world')