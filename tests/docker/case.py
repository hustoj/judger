import os
import tempfile
import unittest

from judge.container import Compiler, Runner
from judge.task import Task
from judge.worker import Environment


class CaseScaffold(unittest.TestCase):
    language_id = 0

    def setUp(self):
        self.init_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp(prefix="tc")
        if os.getenv('DEBUG'):
            print(self.tmp_dir)
        os.chdir(self.tmp_dir)
        self.env = Environment(self.prepare_task())

    def prepare_task(self):
        info = {
            "solution_id": 1000,
            "code": self.get_code(),
            "language": self.get_language(),
            "time_limit": 100,
            "memory_limit": 100,
        }
        task = Task()
        task.load(info)
        return task

    def tearDown(self):
        if os.getcwd() == self.init_dir:
            return
        os.system('rm -rf *')
        os.chdir(self.init_dir)
        os.rmdir(self.tmp_dir)

    def compile_code(self, code):
        compiler = Compiler()
        compiler.compile(self.env)

    def execute(self):
        runner = Runner()
        runner.execute(self.env, self.get_input())

    def get_execute_config(self, language_type):
        return {
            'cpu': 10,
            'memory': 10,
            'language': language_type.language_id,
            'output': 10,
            'verbose': True,
        }

    def get_input(self):
        return '''
1 2
3 4
5 6
'''

    def assertCompileResult(self):
        self.assertTrue(os.path.isfile('compile.out'))
        self.assertTrue(os.path.isfile('compile.err'))
        with open('compile.out') as f:
            content = f.read()
            self.assertEqual("", content)
        with open('compile.err') as f:
            content = f.read()
            self.assertEqual("", content)

        self.assertTrue(os.path.isfile(self.env.task.language_type.execute_name))

    def assertExecuteResult(self):
        self.assertTrue(os.path.isfile('user.out'))
        self.assertTrue(os.path.isfile('user.err'))
        with open('user.out') as f:
            content = f.read()
            print('user.out', content)
            # self.assertEqual("3\n7\n11\n", content)
        with open('user.err') as f:
            content = f.read()
            print('user.err', content)
            # self.assertEqual("", content)

    def get_code(self):
        pass

    def get_language(self):
        return self.language_id
