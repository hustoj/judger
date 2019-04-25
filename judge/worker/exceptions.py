class JudgeException(Exception):
    pass


class ExecuteException(JudgeException):
    def __init__(self, code, user_out, user_err):
        self.code = code
        self.user_out = user_out
        self.user_err = user_err


class TimeLimitException(ExecuteException):
    pass
