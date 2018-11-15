import unittest

from constant import Status
from judge.remote import WebApi, UrlMaster
from result import Result
import requests


class TestJudgeUrl(unittest.TestCase):
    url = ...

    def build_master(self):
        return UrlMaster(self.url)

    def test_url(self):
        self.url = "http://httpbin.org/get/"
        master = self.build_master()
        self.assertEqual(master.base_url, self.url)
        self.assertEqual(master.data, self.url + 'data')
        self.assertEqual(master.report, self.url + 'report')
        self.assertEqual(master.heartbeat, self.url + 'heartbeat')

    def test_not_tail_with_slash(self):
        self.url = "http://httpbin.org/get"
        master = self.build_master()
        self.assertEqual(master.base_url, self.url + '/')


class TestWebApi(unittest.TestCase):
    url = "http://neo.test/judge/api"

    def build_api(self) -> WebApi:
        cfg = {
            'url': self.url,
            "judge_id": "test_id",
            "code": "test_code"
        }
        api = WebApi(cfg)
        api.set_client(requests.Session())
        return api

    def test_get_data(self):
        api = self.build_api()
        result = Result.make(Status.ACCEPTED, 1111)
        response = api.report(result)
        print(response.content)

    def test_report(self):
        api = self.build_api()
        result = Result.make(Status.ACCEPTED, 1111)
        response = api.report(result)
        print(response.content)
