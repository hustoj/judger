import argparse
import logging

from judge import Judged
from judge.config import load_config
from judge.libs import pid


def setup_logger(cfg):
    log = logging.getLogger()

    formatter = logging.Formatter('%(asctime)s %(name)s-%(levelname)s-%(module)s:%(message)s')
    handler = logging.FileHandler(cfg['log_file'])
    handler.setFormatter(formatter)
    log.addHandler(handler)

    if cfg['debug'] or is_debug():
        log.info("debug mode on")
        log.setLevel(logging.DEBUG)
    else:
        log.info("debug mode off")
        log.setLevel(logging.INFO)

    return log


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='judge.toml')
    return parser.parse_args()


def main():
    args = parse_arguments()

    cfg = load_config(args.config)
    log = setup_logger(cfg.judged)

    log.info('Judged Starting...')

    with pid.PIDFile(cfg.judged['pid_file']):
        judge = Judged(cfg)
        judge.run()


if __name__ == '__main__':
    main()
