import unittest

from judge.constant import Status
from judge.result import Result


class TestResult(unittest.TestCase):
    def testParse(self):
        result = Result.make(Status.ACCEPTED, 22)
        d = result.as_dict()

        self.assertEqual(d['result'], Status.ACCEPTED)
        self.assertEqual(d['solution_id'], result.solution_id)