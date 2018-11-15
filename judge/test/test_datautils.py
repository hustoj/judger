import os
import tempfile
import unittest
from unittest.mock import MagicMock

from judge.datautils import DataManager, LocalCache


class MockApi(object):
    indata = 'test in data'
    outdata = 'test out data'

    def get_data(self, pid):
        return {
            'input': self.indata,
            'output': self.outdata
        }


class TestDataUtils(unittest.TestCase):
    path = None
    work_dir = None

    def setUp(self):
        self.path = tempfile.mkdtemp(prefix="td_")

    def tearDown(self):
        os.chdir(self.path)
        os.system("rm -rf *")
        os.rmdir(self.path)

    def test_get_data(self):
        mock = MockApi()

        manager = DataManager()
        local_cache = LocalCache('/tmp/ld/')
        local_cache.write_input = MagicMock()
        local_cache.write_output = MagicMock()
        local_cache.get_input_data = MagicMock(return_value=mock.indata)
        local_cache.get_output_data = MagicMock(return_value=mock.outdata)

        manager.set_cache(local_cache)

        manager.set_provider(mock)
        pid = 1117
        self.assertEqual(manager.get_input(pid), mock.indata)
        self.assertEqual(manager.get_output(pid), mock.outdata)
        local_cache.write_input.assert_called()
        local_cache.write_output.assert_called()
        local_cache.get_input_data.assert_called_once()
        local_cache.get_output_data.assert_called_once()
