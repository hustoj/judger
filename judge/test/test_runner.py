import tempfile
import unittest

from judge.container.runner import Runner
from judge.runner import CaseResult
from judge.task import Task


class TestRunner(unittest.TestCase):
    def testGeneral(self):
        executor = Runner()
        self.assertEqual('runner:v1', executor.image)
        new_name = 'runner:test'
        executor.set_image(new_name)
        self.assertEqual(new_name, executor.image)

        self.assertEqual('runner', executor.command())
        command_name = '/home/judger/Main'
        executor.set_command(command_name)
        self.assertEqual(command_name, executor.command())

    def testReturn(self):
        executor = Runner()
        executor.set_image('runner:test')

        task = Task()
        task.working_dir = tempfile.mkdtemp('runner_test')
        info = {'time_limit': 1, 'memory_limit': 2, 'solution_id': 3}
        task.set_info(info)
        executor.execute(task)
        self.assertTrue(executor.is_ok())
        result = CaseResult()
        result.parse_runner(executor.get_stdout())
        self.assertEqual(result.result, 4)
        self.assertEqual(result.time_cost, 7)
        self.assertEqual(result.memory_cost, 200)
