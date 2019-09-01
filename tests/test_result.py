import unittest

from judge.result import Status, CaseResult


class TestResult(unittest.TestCase):
    def testParse(self):
        result = CaseResult.make(Status.ACCEPTED, 22)
        d = result.as_dict()

        self.assertEqual(d['result'], Status.ACCEPTED)
        self.assertEqual(d['solution_id'], result.solution_id)
