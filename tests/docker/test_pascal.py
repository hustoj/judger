import os

from judge.language import get_language
from tests.docker.case import CaseScaffold


class TestPascal(CaseScaffold):
    language_id = 2

    def test_pascal(self):
        language_type = get_language(self.language_id)
        self.compile_code(self.get_code(), language_type)
        self.assertCompileResult(language_type)

        self.execute(language_type)
        self.assertExecuteResult()

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
