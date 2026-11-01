import json
import unittest
from unittest.mock import patch

import requests

from judge.remote import RemoteRequestFailed, UrlMaster, WebApi
from judge.result import CaseResult, Status


class FakeResponse:
    def __init__(self, body=None, status_code=200, content=None):
        self.status_code = status_code
        if content is None:
            content = b'' if body is None else json.dumps(body).encode()
        self.content = content
        self.text = content.decode() if isinstance(content, bytes) else content

    def json(self):
        return json.loads(self.text)


class FakeClient:
    def __init__(self, responses=None, exception=None):
        self.responses = list(responses or [])
        self.exception = exception
        self.calls = []
        self.closed = False

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if self.exception:
            raise self.exception
        return self.responses.pop(0)

    def close(self):
        self.closed = True


class TestJudgeUrl(unittest.TestCase):
    def test_url(self):
        master = UrlMaster('http://example.test/judge/api/')
        self.assertEqual(master.base_url, 'http://example.test/judge/api/')
        self.assertEqual(master.data, 'http://example.test/judge/api/data')
        self.assertEqual(master.report, 'http://example.test/judge/api/report')
        self.assertEqual(master.heartbeat, 'http://example.test/judge/api/heartbeat')

    def test_not_tail_with_slash(self):
        self.assertEqual(UrlMaster('http://example.test/api').base_url, 'http://example.test/api/')


class TestWebApi(unittest.TestCase):
    cfg = {
        'url': 'https://example.test/judge/api',
        'judge_id': 'judge-1',
        'code': 'secret-code',
        'timeout': 7,
    }

    def build_api(self, response=None, client=None):
        api = WebApi(self.cfg)
        api.set_client(client or FakeClient([response or FakeResponse({'code': 0})]))
        return api

    def test_fixed_signature_matches_php_vector(self):
        payload = {
            'alpha': 'a b',
            'empty': None,
            'multiline': 'line1\nline2',
            'special': 'a&b=c%',
            'unicode': '中文/é',
        }
        self.assertEqual(
            WebApi.signature('secret-code', 'post', '/judge/api/report', payload, 'nonce-fixed'),
            '17781b7c568a1ea004cdec552706d98254b50dcb7d207a332c8840eb46a70062',
        )

    def test_empty_strings_trimmed_and_omitted_from_get_signature_and_wire_payload(self):
        client = FakeClient([FakeResponse([{'input': 'x', 'output': 'y'}])])
        api = self.build_api(client=client)
        with patch('judge.remote.secrets.token_hex', return_value='nonce-empty'):
            response = api._request('GET', api.url_manager.data, {
                'pid': 12, 'ts': 1700000000, 'blank': '  ', 'trimmed': '  value\n',
            })
        self.assertEqual(response.status_code, 200)
        sent = client.calls[0][2]
        self.assertEqual(sent['params'], {'pid': 12, 'ts': 1700000000, 'trimmed': 'value'})
        self.assertEqual(sent['headers']['Nonce'], 'nonce-empty')
        expected = WebApi.signature(
            self.cfg['code'], 'GET', '/judge/api/data', sent['params'], 'nonce-empty'
        )
        self.assertEqual(sent['headers']['Token'], expected)

    def test_get_data_accepts_gzip_decoded_list_response(self):
        body = [{'input': '中文\n', 'output': 'a&b'}, {'input': '', 'output': '特殊字符'}]
        client = FakeClient([FakeResponse(body)])
        response = self.build_api(client=client).get_data(1021)
        self.assertEqual(response.data, body)

    def test_get_data_rejects_invalid_list_item(self):
        client = FakeClient([FakeResponse([{'input': 'only-input'}])])
        with self.assertRaises(RemoteRequestFailed):
            self.build_api(client=client).get_data(1021)

    def test_report_requires_and_forwards_token_without_logging_it(self):
        client = FakeClient([FakeResponse({'code': 0})])
        api = self.build_api(client=client)
        with self.assertRaises(RemoteRequestFailed):
            api.report({'solution_id': 1, 'status': Status.ACCEPTED}, '  ')
        api.report({'solution_id': 1, 'status': Status.ACCEPTED}, ' task-secret ')
        payload = client.calls[0][2]['data']
        self.assertEqual(payload['judge_token'], 'task-secret')
        self.assertNotIn('task-secret', str(client.calls[0][2]['headers']))

    def test_report_maps_legacy_compile_error_and_includes_ts(self):
        client = FakeClient([FakeResponse({'code': 0})])
        api = self.build_api(client=client)
        with patch('judge.remote.time.time', return_value=1700000000):
            api.report({'solution_id': 1, 'status': 11, 'error': '  syntax\nerror  '}, 'token')
        data = client.calls[0][2]['data']
        self.assertEqual(data['compile_info'], 'syntax\nerror')
        self.assertNotIn('error', data)
        self.assertEqual(data['ts'], 1700000000)

    def test_report_forwards_temporary_status(self):
        client = FakeClient([FakeResponse({'code': 0})])
        api = self.build_api(client=client)
        api.report({'solution_id': 1, 'status': Status.COMPILING}, 'token')
        self.assertEqual(client.calls[0][2]['data']['status'], Status.COMPILING)

    def test_heartbeat_accepts_empty_string_response(self):
        client = FakeClient([FakeResponse(content=b'')])
        self.assertIsNone(self.build_api(client=client).heartbeat())

    def test_nonzero_application_code_raises_without_body_logging(self):
        client = FakeClient([FakeResponse({'code': 403, 'message': 'secret-token'})])
        with self.assertRaises(RemoteRequestFailed):
            self.build_api(client=client).report({'solution_id': 1, 'status': 4}, 'token')

    def test_http_error_and_timeout_are_wrapped(self):
        for response in (FakeResponse({'message': 'private'}, status_code=500),):
            with self.assertRaises(RemoteRequestFailed):
                self.build_api(client=FakeClient([response])).heartbeat()
        with self.assertRaises(RemoteRequestFailed):
            self.build_api(client=FakeClient(exception=requests.Timeout())).heartbeat()

    def test_nonce_unique_and_redirects_disabled(self):
        client = FakeClient([FakeResponse({'code': 0}), FakeResponse({'code': 0})])
        api = self.build_api(client=client)
        api.heartbeat()
        api.heartbeat()
        first, second = client.calls
        self.assertNotEqual(first[2]['headers']['Nonce'], second[2]['headers']['Nonce'])
        self.assertFalse(first[2]['allow_redirects'])
        self.assertNotIn('Token', first[2].get('params', {}))
        self.assertNotIn('Token', first[2].get('data', {}))

    def test_destructor_is_safe_on_partial_initialization(self):
        api = object.__new__(WebApi)
        api.__del__()

    def test_close_is_safe_and_idempotent(self):
        client = FakeClient()
        api = self.build_api(client=client)
        api.close()
        api.close()
        self.assertTrue(client.closed)


if __name__ == '__main__':
    unittest.main()
