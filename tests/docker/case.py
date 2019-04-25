import json
import os
import tempfile
import unittest

from judge.compiler.compiler import Compiler
from judge.container.runner import Runner
from judge.utils import write_file


class CaseScaffold(unittest.TestCase):
    def setUp(self):
        self.init_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp(prefix="tc")
        if os.getenv('DEBUG'):
            print(self.tmp_dir)
        os.chdir(self.tmp_dir)

    def tearDown(self):
        if os.getcwd() == self.init_dir:
            return
        os.system('rm -rf *')
        os.chdir(self.init_dir)
        os.rmdir(self.tmp_dir)

    def compile_code(self, code, language_type):
        write_file(language_type.source_name, code)

        write_file('compile.json', json.dumps(language_type.to_compile_info()))

        compiler = Compiler()
        compiler.execute(self.tmp_dir)

    def execute(self, language_type):
        write_file('user.in', self.get_input())
        case_conf = self.get_execute_config(language_type)
        write_file('case.json', json.dumps(case_conf))

        runner = Runner()
        runner.execute(self.tmp_dir)

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

    def assertCompileResult(self, language_type):
        self.assertTrue(os.path.isfile('compile.out'))
        self.assertTrue(os.path.isfile('compile.err'))
        with open('compile.out') as f:
            content = f.read()
            self.assertEqual("", content)
        with open('compile.err') as f:
            content = f.read()
            self.assertEqual("", content)

        self.assertTrue(os.path.isfile(language_type.execute_name))

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
