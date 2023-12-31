import logging
from logging.handlers import TimedRotatingFileHandler
import datetime


def loggerHandler(logger_name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up a Logger with a TimedRotatingFileHandler.

    Parameters:
    - logger_name (str): The name of the logger.
    - log_level (int): The logging level. Defaults to logging.INFO.

    Returns:
    - logging.Logger: The configured Logger object.
    """
    # 获取当前日期作为日志文件名的一部分
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = f'{logger_name}_{current_date}.log'

    # 创建一个Logger对象
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # 创建一个TimedRotatingFileHandler，每天切换日志文件
    file_handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=0)
    file_handler.setLevel(log_level)

    # 定义日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    # 将格式应用于处理程序
    file_handler.setFormatter(formatter)

    # 将处理程序添加到Logger对象
    logger.addHandler(file_handler)

    return logger
