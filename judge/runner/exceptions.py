
from judge.exceptions import JudgeException


class Alarm(JudgeException):
    pass


class ExecuteException(JudgeException):
    pass


class TimeLimitException(ExecuteException):
    pass


def alarm_handler(signum, frame):
    raise Alarm
