import logging
import os


def is_debug():
    return bool(os.getenv('JUDGE_DEBUG'))


class JudgeLogFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith('judge')


def setup_logger(cfg):
    log = logging.getLogger()

    formatter = logging.Formatter('%(asctime)s %(name)s-%(levelname)s-%(module)s:%(message)s')
    handler = logging.FileHandler(cfg['log_file'])
    handler.setFormatter(formatter)
    handler.addFilter(JudgeLogFilter())
    log.addHandler(handler)

    if cfg['debug'] or is_debug():
        log.info("debug mode on")
        log.setLevel(logging.DEBUG)
    else:
        log.info("debug mode off")
        log.setLevel(logging.INFO)

    return log
