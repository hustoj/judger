import os
import json
import tempfile
import unittest

from judge.compiler.compiler import Compiler
from judge.utils import write_file


class CaseScaffold(unittest.TestCase):
    def setUp(self):
        self.init_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp(prefix="tc")
        if os.getenv('DEBUG'):
            print(self.tmp_dir)

    def tearDown(self):
        if os.getcwd() == self.init_dir:
            return
        os.system('rm -rf *')
        os.chdir(self.init_dir)
        os.rmdir(self.tmp_dir)

    def compileCode(self, code, language_type):
        os.chdir(self.tmp_dir)

        write_file(language_type.source_name, code)

        write_file('compile.json', json.dumps(language_type.to_compile_info()))

        compiler = Compiler()
        compiler.execute(self.tmp_dir)
