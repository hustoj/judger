import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock

from judge.data.cache import LocalCache
from judge.data.manager import DataManager
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
        data = {
            'input': 'test in data',
            'output': 'test out data'
        }
        mock = MockApi(json.dumps(data).encode())

        manager = DataManager()
        local_cache = LocalCache('/tmp/ld/')
        local_cache.save_data = MagicMock()
        local_cache.get_data = MagicMock(return_value=mock.get_data)

        manager.set_cache(local_cache)

        manager.set_remote(mock)
        pid = 1117
        ret = manager.get_data(pid)
        self.assertEqual(ret['input'], data['input'])
        self.assertEqual(ret['output'], data['output'])
        local_cache.save_data.assert_called()


class TestLocalCache(unittest.TestCase):
    pass
