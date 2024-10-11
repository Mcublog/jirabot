import logging
from logging import Logger


def build_loger(module_name: str, level: int = logging.INFO) -> Logger:
    logging.basicConfig(format='%(levelname)-8s: %(asctime)s' + ': ' +
                        '%(module)s: %(message)s')
    log = logging.getLogger(module_name)
    log.setLevel(level=logging.INFO)
    return log
