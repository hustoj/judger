import unittest
import tempfile
import json

from judge.runner import get_executor
from judge.task import Task


class TestRunner(unittest.TestCase):
    def testGeneral(self):
        executor = get_executor()
        self.assertEqual('runner:v1', executor.image)
        new_name = 'runner:test'
        executor.set_image(new_name)
        self.assertEqual(new_name, executor.image)

        self.assertEqual('runner', executor.command())
        command_name = '/home/judger/Main'
        executor.set_command(command_name)
        self.assertEqual(command_name, executor.command())

    def testReturn(self):
        executor = get_executor()
        executor.set_image('runner:test')

        tmp_dir = tempfile.mkdtemp('runner_test')
        task = Task()
        info = {'time_limit': 1, 'memory_limit': 2, 'solution_id': 3}
        task.set_info(info)
        ret = executor.execute(task, tmp_dir)
        ret_obj = json.loads(ret)
        self.assertEqual(ret_obj['result'], 4)
        self.assertEqual(ret_obj['time_cost'], 7)
        self.assertEqual(ret_obj['memory_cost'], 200)
