import json

from requests import Session

from judge.log import get_logger
from judge.runner import CaseResult


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
        self._client.headers.update(self._auth_info())

    def _auth_info(self):
        header = {
            'Judge-Code': self.cfg['code']
        }
        return header

    def get_data(self, pid) -> DataResponse:
        log = get_logger()
        log.info('Fetch data of {pid}'.format(pid=pid))
        payload = {'pid': pid}

        r = self._client.get(self.url_manager.data, params=payload)
        if r.status_code != 200:
            log.error('fetch data failed: {r}'.format(r=r.content))
            raise FetchDataFailed()
        log.info('fetch data of {pid}: {content}'.format(pid=pid, content=r.content[:200]))
        return DataResponse(r.content)

    def report(self, result):
        if isinstance(result, CaseResult):
            result = result.as_dict()
        get_logger().info('Report Status %s', json.dumps(result))
        return self._client.post(self.url_manager.report, data=result)

    def heartbeat(self):
        self._client.post(self.url_manager.heartbeat)

    def close(self):
        self._client.close()

    def __del__(self):
        self.close()
