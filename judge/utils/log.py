import logging

from judge.utils import is_debug


def logger() -> logging.Logger:
    return logging.getLogger('judger')


def setup_logger(filename):
    log = logger()

    formatter = logging.Formatter('%(asctime)s %(name)s-%(levelname)s-%(module)s:%(message)s')
    handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)
    log.addHandler(handler)

    if is_debug():
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    return log
