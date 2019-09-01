import json

import pika

from judge.language import LanguageType, get_language


class Task(object):
    info = ...

    @staticmethod
    def from_json(content):
        task = Task()
        task.load(json.loads(content))
        return task

    def load(self, info):
        self.info = info

    @property
    def language_type(self) -> LanguageType:
        return get_language(self.language)

    @property
    def output_limit(self) -> int:
        return 16

    @property
    def task_id(self):
        return self.info['solution_id']

    @property
    def running_command(self):
        return self.language_type.running_command

    @property
    def problem_id(self):
        return self.info['problem_id']

    @property
    def language(self):
        return self.info['language']

    @property
    def is_special(self):
        return self.info['is_special']

    @property
    def code(self):
        return self.info['code']

    @property
    def time_limit(self):
        return self.info['time_limit']

    @property
    def memory_limit(self):
        return self.info['memory_limit']


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

    def get_job(self):
        channel = self.get_channel()
        method_frame, header_frame, body = channel.basic_get(self._config['queue'])
        if method_frame:
            channel.basic_ack(method_frame.delivery_tag)
            return body
        else:
            return None
