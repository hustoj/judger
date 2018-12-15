#!/bin/env python3
# coding: utf8
import json
import os
import os.path

from .remote import DataResponse
from .exceptions import JudgeException
from .remote import WebApi
from .log import get_logger


def get_file_content(path):
    f = open(path)
    data = f.read()
    f.close()
    return data


def write_file(path, content):
    f = open(path, 'w')
    f.write(content)
    f.close()


class InvalidRemoteApi(JudgeException):
    pass


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
        get_logger().info('write {path} data'.format(path=path))
        write_file(path, content.decode())

    def get_data(self, pid):
        path = self._get_data_path(pid)
        get_logger().info('get data of %d, %s', pid, path)
        return get_file_content(path)

    def _get_data_path(self, pid):
        filename = '{pid}.json'.format(pid=pid)

        return os.path.join(self.path, filename)


class DataManager(object):
    _remote: WebApi
    _cache: LocalCache

    def set_cache(self, cache):
        self._cache = cache

    def set_remote(self, api):
        self._remote = api

    def get_data(self, pid):
        if self.is_local_cached(pid):
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

    def is_local_cached(self, pid):
        if self._cache:
            return False
        if self._cache.cached(pid):
            return True
        return False


def new_data_manager(path) -> DataManager:
    manager = DataManager()
    manager.set_cache(LocalCache(path))

    return manager
