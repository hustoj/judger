import logging

from judge import pid

from judge import judged
from judge.utils import parse_arguments, setup_logger
from judge.config import load_config


def main():
    args = parse_arguments()

    cfg = load_config(args.config)
    setup_logger(cfg.judged['log_file'])

    logging.info('Judged Starting...')

    with pid.PIDFile(cfg.judged['pid_file']):
        judge = judged.Judged(cfg)
        judge.run()


if __name__ == '__main__':
    main()
