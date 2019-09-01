from tests.docker.case import CaseScaffold


class TestCPP(CaseScaffold):
    language_id = 1

    def test_cpp(self):
        self.compile_code(self.get_code())
        self.assertCompileResult()

        self.execute()
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
