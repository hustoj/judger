from judge.result import read_user_output
from judge.utils.comparer import Compare


class ResultFiles:
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
        return read_user_output(name)
