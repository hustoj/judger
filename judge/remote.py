import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import quote, urlsplit

import requests
from requests import Session

from judge.result import CaseResult, Status
from judge.utils import JudgeException

# Laravel 13 Str::trim: Unicode whitespace, NUL and INVISIBLE_CHARACTERS.
LARAVEL_TRIM_CHARACTERS = (
    '\0\t\n\v\f\r \u0085\u00a0\u00ad\u034f\u061c\u115f\u1160\u1680'
    '\u17b4\u17b5\u180e\u2000\u2001\u2002\u2003\u2004\u2005\u2006'
    '\u2007\u2008\u2009\u200a\u200b\u200c\u200d\u200e\u200f\u2028'
    '\u2029\u202f\u205f\u2060\u2061\u2062\u2063\u2064\u2065\u206a'
    '\u206b\u206c\u206d\u206e\u206f\u2800\u3000\u3164\ufeff\uffa0'
    '\U0001d159\U0001d173\U0001d174\U0001d175\U0001d176\U0001d177'
    '\U0001d178\U0001d179\U0001d17a\U000e0020'
)


class RemoteRequestFailed(JudgeException):
    pass


class FetchDataFailed(RemoteRequestFailed):
    pass


class InvalidData(FetchDataFailed):
    pass


def new_api(cfg):
    api = WebApi(cfg)
    api.set_client(Session())
    return api


class UrlMaster:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip('/') + '/'

    @property
    def data(self):
        return self.base_url + 'data'

    @property
    def report(self):
        return self.base_url + 'report'

    @property
    def heartbeat(self):
        return self.base_url + 'heartbeat'


class DataResponse:
    def __init__(self, response):
        self.origin = response
        self.data = json.loads(response)

    def is_valid(self):
        if isinstance(self.data, dict):
            return 'input' in self.data and 'output' in self.data
        return isinstance(self.data, list) and all(
            isinstance(item, dict) and 'input' in item and 'output' in item
            for item in self.data
        )

    def to_data(self):
        return self.origin


class WebApi:
    _client = None

    def __init__(self, cfg):
        self.cfg = cfg
        self.url_manager = UrlMaster(cfg['url'])
        self.timeout = cfg.get('timeout', 30)

    def set_client(self, client: Session):
        self._client = client

    @staticmethod
    def _normalize_payload(payload):
        # All API fields are flat scalars. Normalize before both sending and
        # signing, including empty strings Laravel would turn into null.
        normalized = {}
        for key, value in payload.items():
            if isinstance(value, str):
                value = value.strip(LARAVEL_TRIM_CHARACTERS)
            elif isinstance(value, bool):
                value = '1' if value else '0'
            elif value is not None and not isinstance(value, (int, float)):
                raise RemoteRequestFailed('judge payload fields must be scalar')
            if value is not None and value != '':
                normalized[key] = value
        return normalized

    @staticmethod
    def signature(secret, method, path, payload, nonce):
        # Exactly mirrors JudgerAuthenticator::signature on the normalized payload.
        payload = WebApi._normalize_payload(payload)
        pairs = []
        for key in sorted(payload):
            value = payload[key]
            if value is None:
                continue
            if isinstance(value, bool):
                value = '1' if value else '0'
            key_text = quote(str(key), safe='')
            value_text = quote(str(value), safe='')
            pairs.append(f'{key_text}={value_text}')
        canonical = '\n'.join([
            method.upper(), '/' + path.lstrip('/'), '&'.join(pairs), nonce,
        ])
        return hmac.new(
            str(secret).encode('utf-8'), canonical.encode('utf-8'), hashlib.sha256
        ).hexdigest()

    def _auth_headers(self, method, url, payload):
        nonce = secrets.token_hex(16)
        return {
            'Judge-Id': str(self.cfg['judge_id']),
            'Token-Version': '2',
            'Nonce': nonce,
            'Token': self.signature(
                self.cfg['code'], method, urlsplit(url).path, payload, nonce
            ),
        }

    def _request(self, method, url, payload, allow_empty=False):
        if self._client is None:
            raise RemoteRequestFailed('HTTP client is not configured')
        payload = self._normalize_payload(payload)
        kwargs = {
            'headers': self._auth_headers(method, url, payload),
            'timeout': self.timeout,
            # Custom authentication headers must never reach redirect targets.
            'allow_redirects': False,
        }
        kwargs['params' if method == 'GET' else 'data'] = payload
        try:
            response = self._client.request(method, url, **kwargs)
        except requests.RequestException:
            # Exception details can include URLs, credentials or response bodies.
            raise RemoteRequestFailed('judge request failed') from None
        if not 200 <= response.status_code < 300:
            raise RemoteRequestFailed(
                f'judge request returned HTTP {response.status_code}'
            )
        if allow_empty and not response.content:
            return response
        try:
            body = response.json()
        except ValueError:
            raise RemoteRequestFailed('invalid judge API response') from None
        if not isinstance(body, (dict, list)):
            raise RemoteRequestFailed('invalid judge API response')
        if isinstance(body, dict) and 'code' in body and body['code'] not in (0, '0'):
            raise RemoteRequestFailed('judge request rejected')
        return response

    def get_data(self, pid) -> DataResponse:
        response = self._request(
            'GET', self.url_manager.data, {'pid': pid, 'ts': int(time.time())}
        )
        try:
            result = DataResponse(response.content)
        except (TypeError, ValueError):
            raise InvalidData('invalid judge data response') from None
        if not result.is_valid():
            raise InvalidData('invalid judge data response')
        return result

    def report(self, result, judge_token):
        if not isinstance(judge_token, str) or not judge_token.strip(LARAVEL_TRIM_CHARACTERS):
            raise RemoteRequestFailed('judge task token is missing')
        if isinstance(result, CaseResult):
            result = result.as_dict()
        payload = dict(result)
        error = payload.pop('error', None)
        info_field = {
            str(Status.COMPILE_ERROR): 'compile_info',
            str(Status.RUNTIME_ERROR): 'runtime_info',
        }.get(str(payload.get('status')))
        if info_field and error is not None:
            payload.setdefault(info_field, error)
        payload.update(ts=int(time.time()), judge_token=judge_token)
        return self._request('POST', self.url_manager.report, payload)

    def heartbeat(self):
        self._request(
            'POST', self.url_manager.heartbeat, {'ts': int(time.time())}, allow_empty=True
        )

    def close(self):
        client = self._client
        self._client = None
        if client is not None:
            client.close()

    def __del__(self):
        try:
            self.close()
        except BaseException:  # noqa: BLE001
            # Includes partial initialization and this project's BaseException-
            # derived JudgeException; finalizers must never interrupt shutdown.
            pass


if __name__ == '__main__':
    import toml

    cfg = toml.load('../judge.toml')
    remote = new_api(cfg['api'])
    print(remote.get_data(1000).origin)
