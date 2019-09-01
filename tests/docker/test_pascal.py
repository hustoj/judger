import os

from tests.docker.case import CaseScaffold


class TestPascal(CaseScaffold):
    language_id = 2

    def test_pascal(self):
        self.compile_code(self.get_code())
        self.assertCompileResult()

        self.execute()
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

    def assertCompileResult(self):
        self.assertTrue(os.path.isfile('compile.out'))
        self.assertTrue(os.path.isfile('compile.err'))

        self.assertTrue(os.path.isfile(self.env.task.language_type.execute_name))
