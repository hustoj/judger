import unittest
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from requests.exceptions import ReadTimeout

from judge.container.compiler import CompileException, Compiler
from judge.container.executor import DockerExecutor
from judge.result import Status
from judge.worker.worker import Worker


class TestWorkerFailures(unittest.TestCase):
    @patch('judge.worker.worker.Compiler.compile', side_effect=RuntimeError('Docker unavailable'))
    def test_infrastructure_failure_is_not_accepted(self, compile_code):
        worker = Worker()
        worker.prepare = Mock()
        task = Mock(task_id=123)
        with self.assertLogs('judge.worker.worker', level='ERROR'):
            worker.process(task, [])
        self.assertEqual(worker.result.result, Status.RUNTIME_ERROR)
        self.assertEqual(worker.result.as_dict()['runtime_info'], 'Docker unavailable')

    @patch('judge.container.executor.docker.DockerClient')
    def test_docker_wait_uses_task_time_limit(self, client_class):
        container = client_class.return_value.containers.run.return_value
        container.id = 'test-container'
        container.wait.return_value = {'StatusCode': 0}
        executor = DockerExecutor()
        executor.time_limit = 2
        executor.do_execute()
        container.wait.assert_called_once_with(timeout=2)
        self.assertEqual(executor.time_limit, 2)

    @patch('judge.container.executor.docker.DockerClient')
    def test_timeout_removes_only_the_current_container_and_closes_client(self, client_class):
        client = client_class.return_value
        container = client.containers.run.return_value
        container.id = 'timed-out-container'
        container.wait.side_effect = ReadTimeout('Docker wait timed out')
        executor = DockerExecutor()

        with self.assertRaises(ReadTimeout):
            executor.do_execute()

        container.remove.assert_called_once_with(force=True)
        client.close.assert_called_once_with()
        client.containers.prune.assert_not_called()
        self.assertEqual(executor.container_ids, [])

    @patch('judge.container.compiler.DockerExecutor')
    def test_unsuccessful_compiler_json_is_a_compile_error(self, executor_class):
        executor = executor_class.return_value
        executor.get_stdout.return_value = b'{"success": false}'
        executor.get_stderr.return_value = b'compiler rejected source'
        executor.get_status.return_value = 0
        executor.is_ok.return_value = True
        with TemporaryDirectory() as directory:
            environment = Mock(path=directory)
            with self.assertRaisesRegex(CompileException, 'compiler rejected source'):
                Compiler.compile(environment)
