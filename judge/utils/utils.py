import os


def is_debug():
    return bool(os.getenv('JUDGE_DEBUG'))
