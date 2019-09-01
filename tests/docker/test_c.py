from tests.docker.case import CaseScaffold


class TestC(CaseScaffold):
    language_id = 0

    def test_c(self):
        self.compile_code(self.get_code())
        self.assertCompileResult()

        self.execute()
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
