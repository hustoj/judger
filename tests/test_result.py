import unittest

from judge.result import Status, CaseResult


class TestResult(unittest.TestCase):
    def testParse(self):
        result = CaseResult.make(Status.ACCEPTED, 22)
        d = result.as_dict()

        self.assertEqual(d['status'], Status.ACCEPTED)
        self.assertEqual(d['solution_id'], result.solution_id)

    def test_compile_error_uses_server_field(self):
        result = CaseResult.make(Status.COMPILE_ERROR, 22)
        result.error = 'compile failed'
        self.assertEqual(result.as_dict()['compile_info'], result.error)
        self.assertNotIn('error', result.as_dict())

    def test_runtime_error_uses_server_field(self):
        result = CaseResult.make(Status.RUNTIME_ERROR, 22)
        result.error = 'runtime failed'
        self.assertEqual(result.as_dict()['runtime_info'], result.error)

    def test_accepted_result_omits_error_fields(self):
        result = CaseResult.make(Status.ACCEPTED, 22)
        self.assertNotIn('compile_info', result.as_dict())
        self.assertNotIn('runtime_info', result.as_dict())
