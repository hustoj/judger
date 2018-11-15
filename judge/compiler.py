#!/bin/env python3

import logging
import subprocess
from signal import alarm, signal, SIGALRM

from judge.language import LanguageType

MAX_COMPILE_TIME = 3


class CompileException(Exception):
    pass


class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


class Compiler(object):
    language = None
    language_centre = ...
    language_type = ...

    def _writefile(self, code):
        f = open(self.language_type.source_name, 'w')
        f.write(code)
        f.close()

    def compile(self, code, language_type: LanguageType):
        self.language_type = language_type
        self._writefile(code)
        self._compile()

    def _compile(self):
        args = self.language_type.full_compile_command()

        p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        signal(SIGALRM, alarm_handler)
        alarm(MAX_COMPILE_TIME)
        try:
            (stdoutdata, stderrdata) = p.communicate()  # python 3.3 add timeout
            if stderrdata or stdoutdata:
                logging.warning("Executor error: out => %s, err => %s", stdoutdata, stderrdata)
            alarm(0)
            if p.returncode != 0:
                raise CompileException(stderrdata)
        except Alarm:
            p.kill()
            raise CompileException('Exceed Compile Time Limit')
