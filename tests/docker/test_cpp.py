from judge.language import get_language
from tests.docker.case import CaseScaffold


class TestCPP(CaseScaffold):
    language_id = 1

    def test_cpp(self):
        language_type = get_language(self.language_id)
        self.compile_code(self.get_code(), language_type)
        self.assertCompileResult(language_type)

        self.execute(language_type)
        self.assertExecuteResult()

    def get_code(self):
        return """
#include <iostream>
using namespace std;
int main(){
    int a,b;
    while(cin >> a >> b)
        cout << a+b << endl;
    return 0;
}
"""
