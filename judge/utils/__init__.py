import argparse
import os


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='judge.toml')
    return parser.parse_args()


def is_debug():
    return bool(os.getenv('JUDGE_DEBUG'))
