#!/bin/env python3
# coding: utf8

import argparse
import sys

from judge.container.executor import DockerExecutor
from judge.task import Task
from judge.worker import Environment

sys.path.append('.')


def run(task):
    # type: (Task) -> None
    env = Environment(task)
    executor = DockerExecutor()
    executor.execute(env.path)
    print(executor.is_ok())
    print(executor.get_stdout())
    print(executor.get_status())


def main():
    parser = argparse.ArgumentParser(description='Quick execute container task')
    parser.add_argument('--path', metavar='-p', type=str, required=True,
                        help='path to the working dir')
    parser.add_argument('--memory', metavar='-m', type=int, default=10,
                        help='memory limit (default: 10)')

    args = parser.parse_args()

    task = Task()
    task.load({'memory_limit': args.memory, 'solution_id': 10000})
    task.working_dir = args.path

    run(task)


if __name__ == '__main__':
    main()
