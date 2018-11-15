#!/bin/env python3
# coding: utf8
import logging
import os
import os.path
import shutil

from .exceptions import JudgeException
from .remote import WebApi


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
        infile = self._get_data_path(pid, 'in')
        outfile = self._get_data_path(pid, 'out')
        if os.path.exists(infile) and os.path.exists(outfile):
            return True

        return False

    def get_input_data(self, pid):
        path = self._get_data_path(pid, 'in')

        return get_file_content(path)

    def get_output_data(self, pid):
        path = self._get_data_path(pid, 'out')

        return get_file_content(path)

    def _get_data_path(self, pid, ext):
        filename = '{id}.{ext}'.format(id=pid, ext=ext)
        return os.path.join(self.path, str(pid), filename)

    def _create_pid_dir(self, pid):
        dest_dir = os.path.join(self.path, str(pid))
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

    def write_input(self, pid, content):
        self._create_pid_dir(pid)
        path = self._get_data_path(pid, 'in')
        write_file(path, content)

    def write_output(self, pid, content):
        self._create_pid_dir(pid)
        path = self._get_data_path(pid, 'out')
        write_file(path, content)


class DataManager(object):
    _provider: WebApi
    _cache: LocalCache

    def set_cache(self, cache):
        self._cache = cache

    def set_provider(self, api):
        self._provider = api

    def _get_provider(self):
        if self._provider is None:
            raise InvalidRemoteApi

        return self._provider

    def _prepare(self, pid):
        if self._cache.cached(pid):
            return
        logging.info('Data of {pid} is not cached, will fetch from remote'.format(pid=pid))
        response = self._provider.get_data(pid)
        self._cache.write_input(pid, response.get_input())
        self._cache.write_output(pid, response.get_output())

    def get_input(self, pid):
        self._prepare(pid)
        return self._cache.get_input_data(pid)

    def get_output(self, pid):
        self._prepare(pid)
        return self._cache.get_output_data(pid)


def new_data_manager(path) -> DataManager:
    manager = DataManager()
    manager.set_cache(LocalCache(path))

    return manager
