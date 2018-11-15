import os
import tempfile
import unittest

from judge.compiler import Compiler
from judge.language import LanguageType


class TestCompiler(unittest.TestCase):
    tmp_dir = ...
    current_dir = ...

    def setUp(self):
        self.current_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp(prefix="tc")

    def tearDown(self):
        if os.getcwd() == self.current_dir:
            return
        os.system('rm -rf *')
        os.rmdir(self.tmp_dir)

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
        language_type = self._get_language_type()
        compiler = Compiler()
        compiler.compile(code, language_type)
        self.assertTrue(os.path.isfile(language_type.source_name))
        self.assertTrue(os.path.isfile("Main"))

    def _get_language_type(self):
        language_type = LanguageType()
        language_type.source_name = "main.c"
        language_type.compile_command = "gcc"
        language_type.compile_args = ["main.c", "-o", "Main"]
        return language_type
