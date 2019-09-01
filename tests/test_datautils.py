import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock

from judge.data import DataStore
from judge.data.store import LocalCache
from judge.remote import DataResponse


class MockApi(object):

    def __init__(self, data):
        self.data = data

    def get_data(self, pid):
        return DataResponse(self.data)


class TestDataUtils(unittest.TestCase):
    path = None
    init_dir = None
    work_dir = None

    def setUp(self):
        self.init_dir = os.getcwd()
        self.path = tempfile.mkdtemp(prefix="td_")

    def tearDown(self):
        os.chdir(self.path)
        os.system("rm -rf *")
        os.chdir(self.init_dir)
        os.rmdir(self.path)

    def test_get_data(self):
        json_str = '[{"input":"1 2\\n3 4\\n","output":"3\\n7\\n"},{"input":"1 2\\n3 4\\n","output":"3\\n7\\n"}]'
        mock = MockApi(json_str)

        manager = DataStore()
        local_cache = LocalCache('/tmp/ld/')
        local_cache.save_data = MagicMock()
        local_cache.get_data = MagicMock(return_value=mock.get_data)

        manager.set_cache(local_cache)

        manager.set_remote(mock)
        pid = 1117
        ret = manager.get_data(pid)
        data = json.loads(json_str)
        self.assertEqual(ret.get_input(0), data[0]['input'])
        self.assertEqual(ret.get_output(0), data[0]['output'])
        local_cache.save_data.assert_called()


class TestLocalCache(unittest.TestCase):
    pass
