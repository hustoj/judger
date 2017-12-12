#!/bin/env python3

import subprocess
from signal import alarm, signal, SIGALRM

from models import Solutions
from utils import logger

MAX_USER_OUT = 65536


class Alarm(Exception):
    pass


class Result(object):
    result = Solutions.ACCEPTED
    time_cost = 0
    memory_cost = 0
    error = None
    user_out = None

    def __str__(self):
        return "result:{result},time_cost:{time_cost},memory_cost:{memory_cost},error:{error}" \
            .format(result=self.result, time_cost=self.time_cost, memory_cost=self.memory_cost, error=self.error)

    def __repr__(self):
        return self.__str__()


class ExecuteException(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


class Executor(object):
    def __init__(self, time_limit: int):
        self.time_limit = time_limit

    def execute(self):
        args = ["runner"]
        p = subprocess.Popen(args, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        signal(SIGALRM, alarm_handler)
        alarm(self.time_limit * 5)
        try:
            (stdoutdata, stderrdata) = p.communicate()
            if stderrdata or stdoutdata:
                logger.warning("Executor error:", {'out': stdoutdata, 'err': stderrdata})
            if p.returncode != 0:
                return str(stderrdata, 'utf8')
            alarm(0)  # cancel any alarm
            return self.parse_result()
        except Alarm as e:
            logger.error('Alarm Signal received')
            p.kill()
            raise ExecuteException('Time out')

    def parse_result(self):
        result = Result()
        try:
            f = open("result.txt")
            lines = f.readlines()
            result.result = lines[0].strip()
            result.time_cost = int(lines[1].strip())
            result.memory_cost = int(lines[2].strip())
            result.user_out = open("user.out").read(MAX_USER_OUT)
            result.error = open("user.error").read(MAX_USER_OUT)
        except FileNotFoundError as e:
            result.result = Solutions.RUNTIME_ERROR
            result.time_cost = 0
            result.memory_cost = 0
        return result
