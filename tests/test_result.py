import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from judge.result import CaseResult, Status
from judge.worker.result import ResultFiles


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

    def test_memory_uses_cgroup_peak_not_launcher_rusage(self):
        result = CaseResult.make(Status.ACCEPTED, 22)
        result.peak_memory = 1024
        result.rusage_memory = 128000
        self.assertEqual(result.as_dict()['memory_cost'], 1024)

    def test_get_error_missing_file_returns_empty_and_marks_runtime_error(self):
        result = CaseResult.make(Status.ACCEPTED, 22)
        result.time_cost = 100
        result.peak_memory = 512
        result.rusage_memory = 1024
        cwd = os.getcwd()
        with TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                with self.assertLogs('judge.result', level='ERROR'):
                    error = result.get_error()
            finally:
                os.chdir(cwd)
        self.assertEqual(error, '')
        self.assertEqual(result.result, Status.RUNTIME_ERROR)
        self.assertEqual(result.time_cost, 0)
        self.assertEqual(result.peak_memory, 0)
        self.assertEqual(result.rusage_memory, 0)

    def test_user_output_files_replace_invalid_utf8(self):
        result = CaseResult.make(Status.ACCEPTED, 22)
        cwd = os.getcwd()
        with TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                Path('user.out').write_bytes(b'out:\xff\xfe\n')
                Path('user.err').write_bytes(b'err:\xff\xfe\n')
                user_out = ResultFiles.get_user_out()
                user_err = result.get_error()
            finally:
                os.chdir(cwd)
        self.assertEqual(user_out, 'out:\ufffd\ufffd\n')
        self.assertEqual(user_err, 'err:\ufffd\ufffd\n')
