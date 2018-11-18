import json

import pika

from .language import LanguageType


class Task(object):
    _info = ...
    _language = ...

    @staticmethod
    def from_json(content):
        task = Task()
        task.set_info(json.loads(content))
        return task

    def set_info(self, info):
        self._info = info

    def set_language(self, language):
        self._language = language

    def as_task_info(self):
        return {
            'time_limit': self.time_limit,
            'memory_limit': self.memory_limit,
            'language': self.language,
        }

    @property
    def language_type(self) -> LanguageType:
        return self._language

    @property
    def task_id(self):
        return self._info['solution_id']

    @property
    def running_command(self):
        return self.language_type.running_command

    @property
    def problem_id(self):
        return self._info['problem_id']

    @property
    def language(self):
        return self._info['language']

    @property
    def is_special(self):
        return self._info['is_special']

    @property
    def code(self):
        return self._info['code']

    @property
    def time_limit(self):
        return self._info['time_limit']

    @property
    def memory_limit(self):
        return self._info['memory_limit']


class TaskCentre(object):
    _connection = None
    _config = None
    _channel = None

    def __init__(self, config):
        self._config = config

    def _get_connection(self):
        if self._connection is None:
            credentials = pika.PlainCredentials(self._config['username'], self._config['password'])
            parameters = pika.ConnectionParameters(host=self._config['host'], port=self._config['port'],
                                                   virtual_host=self._config['vhost'],
                                                   credentials=credentials)

            self._connection = pika.BlockingConnection(parameters)

        return self._connection

    def get_channel(self):
        if self._channel is None:
            self._channel = self._get_connection().channel()

        return self._channel

    def next(self):
        channel = self.get_channel()
        method_frame, header_frame, body = channel.basic_get(self._config['queue'])
        if method_frame:
            channel.basic_ack(method_frame.delivery_tag)
            return body
        else:
            return None
