import json
import os
import tempfile
import unittest

from judge.compiler.compiler import Compiler
from judge.language import get_language
from judge.utils import write_file


class TestCPP(unittest.TestCase):
    def setUp(self):
        self.init_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp(prefix="tc")
        # print(self.tmp_dir)

    def tearDown(self):
        if os.getcwd() == self.init_dir:
            return
        os.system('rm -rf *')
        os.chdir(self.init_dir)
        os.rmdir(self.tmp_dir)

    def testCompileC(self):
        code = """
#include <iostream>
using namespace std;
int main(){
    int a,b;
    while(cin >> a >> b)
        cout << a+b << endl;
    return 0;
}
"""
        os.chdir(self.tmp_dir)
        language_type = get_language(1)
        self.prepare(code, language_type)

        self.assertCompileResult(language_type)

    def prepare(self, code, language_type):
        os.chdir(self.tmp_dir)

        write_file(language_type.source_name, code)

        write_file('compile.json', json.dumps(language_type.to_compile_info()))

        compiler = Compiler()

        compiler.execute(self.tmp_dir)
        self.assertCompileResult(language_type)

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
