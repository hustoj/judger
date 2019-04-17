from judge.language import get_language
from tests.compiler import TestC


class TestJava(TestC):
    language_id = 3

    def testCompileC(self):
        language_type = get_language(self.language_id)
        self.do_compile(language_type)
        self.assertCompileResult(language_type)

    def get_code(self):
        return """
import java.util.Scanner;

public class Main{
	public static void main(String args[]){
		Scanner cin = new Scanner(System.in);
		int a, b;
		while (cin.hasNext()){
			a = cin.nextInt();
			b = cin.nextInt();
			System.out.println(a + b);
		}
	}
}
"""
