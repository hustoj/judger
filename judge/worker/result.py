from judge.result import MAX_USER_OUT
from judge.utils.comparer import Compare


class ResultFiles(object):
    @staticmethod
    def get_user_out():
        return ResultFiles.read_file('user.out')

    @staticmethod
    def get_error():
        return ResultFiles.read_file('user.err')

    @staticmethod
    def compare_output(standard):
        comparator = Compare()
        return comparator.compare(standard, ResultFiles.get_user_out())

    @staticmethod
    def read_file(name):
        with open(name) as f:
            content = f.read(MAX_USER_OUT)
        return content
