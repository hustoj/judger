import json
import unittest
from unittest.mock import Mock, patch

from judge.judged import Judged
from judge.result import CaseResult, Status
from judge.task import Task
from judge.utils import JudgeException


class TestJudgeTaskToken(unittest.TestCase):
    def setUp(self):
        self.daemon = Judged.__new__(Judged)
        self.daemon.api = Mock()
        self.daemon.dataProvider = Mock()
        self.daemon.is_support = Mock(return_value=True)
        self.job = {
            'solution_id': 123,
            'problem_id': 1000,
            'language': 1,
            'judge_token': 'private-task-token',
            'code': 'private source code',
        }

    def test_task_preserves_token(self):
        task = Task.from_json(json.dumps(self.job))
        self.assertEqual(task.judge_token, 'private-task-token')

    @patch('judge.judged.Worker')
    def test_report_includes_task_token(self, worker_class):
        worker_class.return_value.has_exception = False
        result = CaseResult.make(Status.ACCEPTED, 123)
        worker_class.return_value.get_result.return_value = result

        self.daemon.handle(json.dumps(self.job))

        self.daemon.api.report.assert_called_once_with(result, 'private-task-token')

    @patch('judge.judged.Worker')
    def test_missing_token_does_not_compile_or_report(self, worker_class):
        del self.job['judge_token']
        with self.assertLogs('judge.judged', level='ERROR') as logs:
            self.daemon.handle(json.dumps(self.job))

        worker_class.assert_not_called()
        self.daemon.api.report.assert_not_called()
        self.assertNotIn('private source code', '\n'.join(logs.output))

    @patch('judge.judged.Worker')
    def test_invalid_token_type_does_not_compile(self, worker_class):
        self.job['judge_token'] = 123
        with self.assertLogs('judge.judged', level='ERROR'):
            self.daemon.handle(json.dumps(self.job))
        worker_class.assert_not_called()

    @patch('judge.judged.Worker')
    def test_failed_report_does_not_log_source_or_task_token(self, worker_class):
        worker_class.return_value.has_exception = False
        self.daemon.api.report.side_effect = JudgeException('Report rejected')
        with self.assertLogs('judge.judged', level='ERROR') as logs:
            self.daemon.handle(json.dumps(self.job))

        output = '\n'.join(logs.output)
        self.assertIn('123', output)
        self.assertNotIn(self.job['judge_token'], output)
        self.assertNotIn(self.job['code'], output)

    @patch('judge.judged.Worker')
    def test_runtime_failure_still_reports_terminal_result(self, worker_class):
        result = CaseResult.make(Status.RUNTIME_ERROR, 123)
        worker_class.return_value.has_exception = True
        worker_class.return_value.get_result.return_value = result

        self.daemon.handle(json.dumps(self.job))

        self.daemon.api.report.assert_called_once_with(result, 'private-task-token')
