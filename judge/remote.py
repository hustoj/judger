import hashlib
import json
import logging
import time

import requests
import toml
from requests import Session

from judge.result import CaseResult

LOGGER = logging.getLogger(__name__)


class FetchDataFailed(Exception):
    pass


def new_api(cfg):
    client = Session()
    api = WebApi(cfg)
    api.set_client(client)

    return api


class UrlMaster(object):
    base_url = ...

    def __init__(self, base_url: str) -> None:
        super().__init__()
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url

    @property
    def data(self):
        return self.base_url + 'data'

    @property
    def report(self):
        return self.base_url + 'report'

    @property
    def heartbeat(self):
        return self.base_url + 'heartbeat'


class InvalidData(BaseException):
    pass


class DataResponse(object):
    def __init__(self, response):
        self.origin = response
        self.data = json.loads(response)

    def is_valid(self):
        return 'input' in self.data and 'output' in self.data

    def to_data(self):
        return self.origin


class WebApi(object):
    _client = ...

    def __init__(self, cfg):
        self.cfg = cfg
        self.url_manager = UrlMaster(cfg['url'])

    def set_client(self, client: Session):
        self._client = client

    def _auth_info(self, ts):
        header = {
            'Judge-Id': self.cfg['judge_id'],
            'Token': self.make_token(ts)
        }
        return header

    def make_token(self, ts):
        origin = "{code}-{ts}".format(code=self.cfg['code'], ts=ts)
        m = hashlib.md5()
        m.update(origin.encode())
        s = m.hexdigest()
        return s

    def get_data(self, pid) -> DataResponse:
        LOGGER.info('Fetch data of {pid}'.format(pid=pid))

        ts = self.prepare_client()
        payload = {
            'pid': pid,
            'ts': ts,
        }
        r = self._client.get(self.url_manager.data, params=payload)
        if r.status_code != 200:
            LOGGER.error('fetch data failed: {r}'.format(r=r.content))
            raise FetchDataFailed()
        LOGGER.info('fetch data of {pid}: {content}'.format(pid=pid, content=r.content[:200]))
        return DataResponse(r.content)

    def report(self, result):
        ts = self.prepare_client()
        if isinstance(result, CaseResult):
            result = result.as_dict()
        LOGGER.info('Report Status %s', json.dumps(result))
        return self._client.post(self.url_manager.report, params={'ts': ts}, data=result)

    def heartbeat(self):
        ts = self.prepare_client()
        self._client.post(self.url_manager.heartbeat, params={'ts': ts})

    def prepare_client(self):
        ts = int(time.time())
        self._client.headers.update(self._auth_info(ts))
        return ts

    def close(self):
        self._client.close()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    cfg = toml.load('../judge.toml')
    remote = WebApi(cfg['api'])
    remote.set_client(requests.Session())
    print(remote.get_data(1000).origin)
