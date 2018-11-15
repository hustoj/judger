import unittest

from judge.comparer import strip_line, Compare
from judge.constant import Status


class TestStripLine(unittest.TestCase):
    def testStripSpace(self):
        self.assertEqual(strip_line("123 456"), "123456")

    def testStripTab(self):
        self.assertEqual(strip_line("123\t456"), "123456")

    def testStripLn(self):
        self.assertEqual(strip_line("123\n456"), "123456")


class TestComparer(unittest.TestCase):
    def test_strip_line(self):
        self.assertEqual('', strip_line('\n'))
        self.assertEqual('', strip_line('\t'))
        self.assertEqual('', strip_line('\t\n'))

    def test_without_blank(self):
        self.assertEqual('12', strip_line('1\t2'))
        self.assertEqual('6557', strip_line('6\t55\n7'))
        self.assertEqual('9', strip_line('\t\n9'))

    def test_comparer(self):
        comparer = Compare()
        self.assertEqual(Status.WRONG_ANSWER, comparer.compare('', '1'))
        self.assertEqual(Status.WRONG_ANSWER, comparer.compare('2', '1'))
        self.assertEqual(Status.PRESENTATION_ERROR, comparer.compare('5\t6', '56'))
        self.assertEqual(Status.PRESENTATION_ERROR, comparer.compare('aaaa', 'aa aa  '))
        self.assertEqual(Status.PRESENTATION_ERROR, comparer.compare('aa\nbb', 'aa\n\nbb'))
        self.assertEqual(Status.ACCEPTED, comparer.compare('56', '56'))
        self.assertEqual(Status.ACCEPTED, comparer.compare('56', '56\t'))


if __name__ == '__main__':
    unittest.main()
