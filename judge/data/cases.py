import json
import logging

from judge.utils import JudgeException

LOGGER = logging.getLogger(__name__)


class DataException(JudgeException):
    pass


class InvalidDataCase(DataException):
    pass


class CaseManager(object):
    def __init__(self, cases):
        if isinstance(cases, (bytes, str)):
            self.cases = json.loads(cases)
        else:
            self.cases = cases
        self.validate()

    def validate(self):
        for item in self.cases:
            if 'input' not in item or 'output' not in item:
                raise InvalidDataCase

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index == self.count:
            raise StopIteration

        data = self.cases[self.index]
        self.index = self.index + 1
        return data

    @property
    def count(self):
        return len(self.cases)

    def get_input(self, index):
        if index > self.count:
            return None
        return self.cases[index]['input']

    def get_output(self, index):
        if index > self.count:
            return None
        return self.cases[index]['output']
