import os

from judge.language import get_language
from .test_c import TestC


class TestPascal(TestC):
    def testCompile(self):
        code = '''
program p1001(Input,Output);
var
  a,b:Integer;
begin
   while not eof(Input) do
     begin
       Readln(a,b);
       Writeln(a+b);
     end;
end.
'''
        os.chdir(self.tmp_dir)
        language_type = get_language(2)
        self.prepare(code, language_type)

        self.assertCompileResult(language_type)

    def assertCompileResult(self, language_type):
        self.assertTrue(os.path.isfile('compile.out'))
        self.assertTrue(os.path.isfile('compile.err'))

        self.assertTrue(os.path.isfile(language_type.execute_name))
