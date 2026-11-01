from judge.language import load_languages

from .test_c import TestC
from .test_cpp import TestCPP
from .test_java import TestJava
from .test_pascal import TestPascal

__all__ = ["TestC", "TestCPP", "TestJava", "TestPascal"]

load_languages()
