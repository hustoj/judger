from judge.exceptions import JudgeException
from .docker import DockerExecutor
from .native import NativeExecutor


def get_executor(type):
    if type == 'docker':
        return DockerExecutor()
    if type == 'native':
        return NativeExecutor()


class Alarm(JudgeException):
    pass


class ExecuteException(JudgeException):
    pass


class TimeLimitException(ExecuteException):
    pass


def alarm_handler(signum, frame):
    raise Alarm
