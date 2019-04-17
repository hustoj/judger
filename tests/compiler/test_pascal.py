import os

from judge.language import get_language
from tests.compiler import TestC


class TestPascal(TestC):
    language_id = 2

    def testCompile(self):
        language_type = get_language(self.language_id)
        self.do_compile(language_type)
        self.assertCompileResult(language_type)

    def get_code(self):
        return '''
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

    def assertCompileResult(self, language_type):
        self.assertTrue(os.path.isfile('compile.out'))
        self.assertTrue(os.path.isfile('compile.err'))

        self.assertTrue(os.path.isfile(language_type.execute_name))
