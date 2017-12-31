#!/bin/env python3
# coding: utf8

import argparse
import logging
import os

from .config import load_config


def get_config_path():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()
    return args.config


def get_logger(filename):
    logging.basicConfig(filename=filename,
                        format='%(asctime)s %(name)s-%(levelname)s-%(module)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S %p',
                        level=logging.INFO)
    return logging


def is_debug():
    return os.getenv('JUDGE_DEBUG')


cfg = load_config(get_config_path())

logger = get_logger(cfg.server.log_file)

if __name__ == '__main__':
    pass
