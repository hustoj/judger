#!/bin/env python3

import multiprocessing
import subprocess
from signal import alarm, signal, SIGALRM

from .utils import logger

MAX_EXECUTE_TIME = 30


class Alarm(Exception):
    pass


class ExecuteException(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


class Executor(object):
    """

    """

    def execute(self, args, inputdata):
        multiprocessing.Process(target=self.do_run, args=(args, inputdata))

    def do_run(self, args, inputdata):
        p = subprocess.Popen(args, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        signal(SIGALRM, alarm_handler)
        alarm(MAX_EXECUTE_TIME)
        try:
            (stdoutdata, stderrdata) = p.communicate(inputdata)
            print(stdoutdata, stderrdata)
            if p.returncode != 0:
                return str(stderrdata, 'utf8')
            alarm(0)  # cancel any alarm
            return stdoutdata
        except Alarm as e:
            logger.error('Alarm Signal received')
            p.kill()
            raise ExecuteException('Time out')
