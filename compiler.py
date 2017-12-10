#!/bin/env python3

import subprocess
from signal import alarm, signal, SIGALRM

from utils import logger

MAX_COMPILE_TIME = 3


class CompileException(Exception):
    pass


class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


class Compiler(object):
    config = None
    code = None

    def writefile(self):
        filename = 'Main.' + self.config['ext']
        f = open(filename, 'w')
        f.write(self.code)
        f.close()

    def compile(self, code, config):
        self.code = code
        self.config = config
        self.writefile()
        return self.do_compile()

    def do_compile(self):
        args = self.config['args']
        # os.execvp(args[0], args)

        p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        signal(SIGALRM, alarm_handler)
        alarm(MAX_COMPILE_TIME)
        try:
            (stdoutdata, stderrdata) = p.communicate()  # python 3.3 add timeout
            if stderrdata or stdoutdata:
                logger.warning("Executor error:", {'out': stdoutdata, 'err': stderrdata})
            alarm(0)
            if p.returncode != 0:
                return str(stderrdata, 'utf8')
        except Alarm:
            p.kill()

        return None
