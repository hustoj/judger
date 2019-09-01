import logging
import os

from judge.remote import WebApi, DataResponse
from judge.utils import write_file, get_file_content

from .cases import CaseManager

LOGGER = logging.getLogger(__name__)


class LocalCache(object):
    def __init__(self, path) -> None:
        super().__init__()
        self.path = path

    def cached(self, pid):
        if os.path.exists(self._get_data_path(pid)):
            return True
        return False

    def save_data(self, pid, content):
        # type: (int, bytes) -> None
        path = self._get_data_path(pid)
        LOGGER.info('write {path} data'.format(path=path))
        write_file(path, content.decode())

    def get_data(self, pid):
        path = self._get_data_path(pid)
        LOGGER.info('get data of %d, %s', pid, path)
        return get_file_content(path)

    def _get_data_path(self, pid):
        filename = '{pid}.json'.format(pid=pid)

        return os.path.join(self.path, filename)


class DataStore(object):
    remote: WebApi
    cache: LocalCache

    def set_cache(self, cache):
        self.cache = cache

    def set_remote(self, api):
        self.remote = api

    def get_data(self, pid):
        """
        :param pid:
        :return: judge.data.CaseManager
        """
        if self.is_cached(pid):
            return CaseManager(self.cache.get_data(pid))

        LOGGER.info('Data of {pid} is not cached, will fetch from remote'.format(pid=pid))
        return CaseManager(self.fetch_data(pid))

    def fetch_data(self, pid):
        response = self.remote.get_data(pid)
        self.write_data(pid, response)

        return response.to_data()

    def write_data(self, pid, response):
        # type: (int, DataResponse) -> None
        if self.cache:
            self.cache.save_data(pid, response.to_data())

    def is_cached(self, pid):
        if self.cache is None:
            return False
        if self.cache.cached(pid):
            return True
        return False
