
from judge import Judged
from judge.utils import parse_arguments
from judge.libs import pid
from judge.utils.log import setup_logger
from judge.config import load_config


def main():
    args = parse_arguments()

    cfg = load_config(args.config)
    log = setup_logger(cfg.judged['log_file'])

    log.info('Judged Starting...')

    with pid.PIDFile(cfg.judged['pid_file']):
        judge = Judged(cfg)
        judge.run()


if __name__ == '__main__':
    main()
