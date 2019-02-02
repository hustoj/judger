class JudgeException(Exception):
    pass


class ExecuteException(JudgeException):
    pass


class TimeLimitException(ExecuteException):
    pass
