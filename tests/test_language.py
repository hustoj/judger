import unittest

from judge.language import LanguageCentre


class TestLanguage(unittest.TestCase):
    def test_parse_language(self):
        language = {
            "language_id": 1,
            "source_name": "Main.cpp",
            "compile_command": "g++",
            "execute_name": "main",
            "compile_args": ["Main.cpp", "-o", "Main", "-fno-asm", "-O2", "-Wall", "-lm", "--static"],
            "running_command": "./main",
            "running_args": "",
        }
        language_centre = LanguageCentre({'language': [language]})

        language_type = language_centre.get_language(1)
        self.assertEqual(language_type.source_name, "Main.cpp")
        self.assertEqual(language_type.compile_command, "g++")
        self.assertEqual(language_type.execute_name, "main")
        self.assertEqual(language_type.compile_args, language['compile_args'])
