#!/bin/env python3
# coding: utf8

import argparse

from judge.runner import get_executor
from judge.task import Task


def run(task, sandbox):
    # type: (Task, str) -> None
    executor = get_executor()
    executor.execute(task, sandbox)


def main():
    parser = argparse.ArgumentParser(description='Quick execute docker task')
    parser.add_argument('--path', metavar='-p', type=str, required=True,
                        help='path to the working dir')
    parser.add_argument('--memory', metavar='-m', type=int, default=10,
                        help='memory limit (default: 10)')

    args = parser.parse_args()

    task = Task()
    task.set_info({'memory_limit': args.memory, 'solution_id': 10000})

    run(task, args.path)


if __name__ == '__main__':
    main()
