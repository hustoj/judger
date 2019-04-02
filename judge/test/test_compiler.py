import os
import tempfile
import unittest

from judge.compiler import Compiler
from judge.language import LanguageType
from task import Task


class TestCompiler(unittest.TestCase):
    def setUp(self):
        self.init_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp(prefix="tc")

    def tearDown(self):
        if os.getcwd() == self.init_dir:
            return
        os.system('rm -rf *')
        os.rmdir(self.tmp_dir)
        os.chdir(self.init_dir)

    def testCompileC(self):
        code = """
#include <stdio.h>
int main(){
    int a,b;
    while(scanf("%d %d",&a, &b) != EOF)
        printf("%d\\n",a+b);
    return 0;
}
"""
        os.chdir(self.tmp_dir)
        f = open('source.c', 'w')
        f.write(code)
        f.close()

        language_type = self._get_language_type()
        compiler = Compiler()
        task = Task()
        task.working_dir = self.tmp_dir
        info = {'time_limit': 1, 'memory_limit': 2, 'solution_id': 3}
        task.set_info(info)
        compiler.execute(task)
        self.assertTrue(os.path.isfile(language_type.source_name))
        self.assertTrue(os.path.isfile("Main"))

    def _get_language_type(self):
        language_type = LanguageType()
        language_type.source_name = "main.c"
        language_type.compile_command = "gcc"
        language_type.compile_args = ["main.c", "-o", "Main"]
        return language_type
