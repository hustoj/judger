import os

from judge.language import get_language
from tests.compiler.case import CaseScaffold


class TestC(CaseScaffold):
    language_id = 0

    def do_compile(self, language_type):
        os.chdir(self.tmp_dir)
        self.compileCode(self.get_code(), language_type)

    def testC(self):
        language_type = get_language(self.language_id)
        self.do_compile(language_type)
        self.assertCompileResult(language_type)

    def get_code(self):
        return """
#include <stdio.h>
int main(){
    int a,b;
    while(scanf("%d %d",&a, &b) != EOF)
        printf("%d\\n",a+b);
    return 0;
}
"""

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
