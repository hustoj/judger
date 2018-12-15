#!/bin/env python3
# coding: utf8

import argparse
import os


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='judge.toml')
    return parser.parse_args()


def is_debug():
    return bool(os.getenv('JUDGE_DEBUG'))


if __name__ == '__main__':
    pass
