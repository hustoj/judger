#!/bin/env python3
import logging

from docker.errors import DockerException

from .executor import DockerExecutor

LOGGER = logging.getLogger(__name__)
MAX_COMPILE_TIME = 3


class CompileException(Exception):
    pass


class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


class Compiler(object):
    @staticmethod
    def compile(env):
        """
        :param judge.worker.enviro.Environment env:
        :return:
        """
        try:
            compiler = DockerExecutor()
            compiler.set_image(env.task.language_type.compile_image)
            compiler.set_command("compiler")
            compiler.execute(env.path)
            LOGGER.info('Compiler: Task %d finished, result: %s', env.task.task_id, compiler.get_status())
            LOGGER.debug('Compiler stdout: %s', compiler.get_stdout())
            # todo: check target is ok
            # self.check_result(task.language_type.target_name)
        except DockerException as err:
            LOGGER.error('Docker Exception:', err)
            raise RuntimeError("Docker execute failed {err}".format(err=err))
