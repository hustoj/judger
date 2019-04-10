#!/bin/env python3

import subprocess
from signal import alarm, signal, SIGALRM

from docker.errors import DockerException

from judge.container.compiler import Compiler
from judge.utils.log import logger

MAX_COMPILE_TIME = 3


class CompileException(Exception):
    pass


class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


class CompilerMaster(object):
    def compile(self, task):
        """
        :param judge.task.Task task:
        :return:
        """
        try:
            compiler = Compiler()
            compiler.execute(task.working_dir)
            logger().info('Compiler: Task %d finished, result: %s', task.task_id, compiler.get_status())
            logger().info('Compiler stdout: %s', compiler.get_stdout())
            # todo: check target is ok
            # self.check_result(task.language_type.target_name)
        except DockerException as err:
            logger().error('Docker Exception:', err)

    # def check_result(self, name):
    #     if os.file_exist():
    #         return True
    #     return false


class Compiler2(object):
    language_type = ...

    def compile(self, task):
        self.language_type = task.language_type
        self._compile()

    def _compile(self):
        args = self.language_type.full_compile_command()
        logger = logger()
        logger.debug('Compile task use {args}'.format(args=args))
        p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        signal(SIGALRM, alarm_handler)
        alarm(MAX_COMPILE_TIME)
        try:
            (stdoutdata, stderrdata) = p.communicate()  # python 3.3 add timeout
            if stderrdata or stdoutdata:
                logger.warning("Compile alert: out => %s, err => %s", stdoutdata, stderrdata)
            alarm(0)
            if p.returncode != 0:
                raise CompileException(stderrdata)
        except Alarm:
            p.kill()
            raise CompileException('Exceed Compile Time Limit')
