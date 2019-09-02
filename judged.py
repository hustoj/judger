import argparse

from judge.judged import Judged
from judge.config import load_config
from judge.libs import pid
from judge.utils import setup_logger


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
