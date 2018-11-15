#!/bin/env python3
# coding: utf8

import argparse
import logging
import os


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='judge.toml')
    return parser.parse_args()


def setup_logger(filename):
    logging.basicConfig(filename=filename,
                        format='%(asctime)s %(name)s-%(levelname)s-%(module)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S %p',
                        level=logging.INFO)
    return logging


def is_debug():
    return os.getenv('JUDGE_DEBUG')


if __name__ == '__main__':
    pass
