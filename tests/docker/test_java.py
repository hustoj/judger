from tests.docker.case import CaseScaffold


class TestJava(CaseScaffold):
    language_id = 3

    def test_java(self):
        self.skipTest('not implement')
        self.compile_code(self.get_code())
        self.assertCompileResult()

        self.execute()
        self.assertExecuteResult()

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

    def get_execute_config(self, language_type):
        return {
            'cpu': 10,
            'memory': 100,
            'language': language_type.language_id,
            'output': 10,
            'verbose': True,
        }
