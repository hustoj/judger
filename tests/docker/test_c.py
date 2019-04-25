import os

from judge.language import get_language
from tests.docker.case import CaseScaffold


class TestC(CaseScaffold):
    language_id = 0

    def test_c(self):
        language_type = get_language(self.language_id)
        self.compile_code(self.get_code(), language_type)
        self.assertCompileResult(language_type)

        self.execute(language_type)
        self.assertExecuteResult()


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
