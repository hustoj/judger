import json

from judge.data.cache import LocalCache
from judge.log import get_logger
from judge.remote import WebApi, DataResponse


class DataManager(object):
    _remote: WebApi
    _cache: LocalCache

    def set_cache(self, cache):
        self._cache = cache

    def set_remote(self, api):
        self._remote = api

    def get_data(self, pid):
        if self.is_cached(pid):
            data = self.read_data(pid)
            return json.loads(data)

        get_logger().info('Data of {pid} is not cached, will fetch from remote'.format(pid=pid))
        response = self._remote.get_data(pid)
        self.write_data(pid, response)

        return json.loads(response.to_data())

    def read_data(self, pid):
        return self._cache.get_data(pid)

    def write_data(self, pid, response):
        # type: (int, DataResponse) -> None
        if self._cache:
            self._cache.save_data(pid, response.to_data())

    def is_cached(self, pid):
        if self._cache is None:
            return False
        if self._cache.cached(pid):
            return True
        return False
