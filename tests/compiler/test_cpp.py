from judge.language import get_language
from tests.compiler import TestC


class TestCPP(TestC):
    language_id = 1

    def testC(self):
        language_type = get_language(self.language_id)
        self.do_compile(language_type)
        self.assertCompileResult(language_type)

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
