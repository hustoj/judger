import logging
import os

from judge.remote import DataResponse, WebApi
from judge.utils import get_file_content, write_file

from .cases import CaseManager

LOGGER = logging.getLogger(__name__)


class LocalCache:
    def __init__(self, path) -> None:
        super().__init__()

        if not os.path.exists(path):
            os.makedirs(path)
        self.path = path

    def cached(self, pid):
        if os.path.exists(self._get_data_path(pid)):
            return True
        return False

    def save_data(self, pid: int, content: bytes) -> None:
        path = self._get_data_path(pid)
        LOGGER.info('write %s data', path)
        write_file(path, content.decode())

    def get_data(self, pid: int):
        path = self._get_data_path(pid)
        LOGGER.info('get data of %d, %s', pid, path)
        return get_file_content(path)

    def _get_data_path(self, pid):
        filename = f'{pid}.json'

        return os.path.join(self.path, filename)


class DataStore:
    remote: WebApi
    cache: LocalCache

    def set_cache(self, cache: LocalCache):
        self.cache = cache

    def set_remote(self, api):
        self.remote = api

    def get_data(self, pid: int) -> CaseManager:
        if self.is_cached(pid):
            return CaseManager(self.cache.get_data(pid))

        LOGGER.info('Data of %s is not cached, will fetch from remote', pid)
        return CaseManager(self.fetch_data(pid))

    def fetch_data(self, pid: int):
        response = self.remote.get_data(pid)
        self.write_data(pid, response)

        return response.to_data()

    def write_data(self, pid: int, response: DataResponse) -> None :
        if self.cache:
            self.cache.save_data(pid, response.to_data())

    def is_cached(self, pid):
        if self.cache is None:
            return False
        if self.cache.cached(pid):
            return True
        return False


def new_data_provider(path, api) -> DataStore:
    manager = DataStore()
    manager.set_cache(LocalCache(path))
    manager.set_remote(api)

    return manager
