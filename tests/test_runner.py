import unittest

from judge.container.executor import DockerExecutor
from judge.result import CaseResult
from judge.task import Task
from judge.worker import Environment


class TestRunner(unittest.TestCase):
    def testGeneral(self):
        executor = DockerExecutor()
        new_name = 'runner:test'
        executor.set_image(new_name)
        self.assertEqual(new_name, executor.image)

        command_name = '/home/judger/Main'
        executor.set_command(command_name)
        self.assertEqual(command_name, executor.command())

    def testReturn(self):
        self.skipTest('not finished')
        executor = DockerExecutor()
        executor.set_image('runner:test')

        task = Task()
        env = Environment(task)
        # task.working_dir = tempfile.mkdtemp('runner_test')
        info = {'time_limit': 1, 'memory_limit': 2, 'solution_id': 3}
        task.load(info)
        executor.execute(env.path)
        self.assertTrue(executor.is_ok())
        result = CaseResult()
        result.parse_runner(executor.get_stdout())
        self.assertEqual(result.result, 4)
        self.assertEqual(result.time_cost, 7)
        self.assertEqual(result.peak_memory, 200)
