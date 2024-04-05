import logging
from logging import FileHandler
from enum import Enum


class Levels(Enum):
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0


def logger(name: str = 'basic', level: Levels = Levels.DEBUG):

    logging.basicConfig(level=level.value)

    logger = logging.getLogger(name)
    logger.setLevel(level.value)

    handler = FileHandler(
        filename=name,
        mode='a',
        encoding='UTF-8'
    )
    handler.setLevel(level.value)
    formatter = logging.Formatter(
        fmt='%(levelname)s - %(asctime)s - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


if __name__ == '__main__':
    logger = logger(name='test.log')
    logger.debug('Debug')
    logger.info('Info')
    logger.warning('Warning')
    logger.critical('Prueba')
