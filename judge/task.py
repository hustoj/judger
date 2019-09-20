import json
import logging

import pika
from pika.exceptions import AMQPConnectionError

from judge.language import LanguageType, get_language

LOGGER = logging.getLogger(__name__)


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

    def __init__(self, config):
        self._config = config

    def _get_connection(self):
        if self._connection is None or self._connection.is_closed:
            credentials = pika.PlainCredentials(self._config['username'], self._config['password'])
            parameters = pika.ConnectionParameters(host=self._config['host'], port=self._config['port'],
                                                   virtual_host=self._config['vhost'],
                                                   credentials=credentials)

            self._connection = pika.BlockingConnection(parameters)

        return self._connection

    def get_channel(self):
        return self._get_connection().channel()

    def get_job(self):
        try:
            channel = self.get_channel()
            method_frame, header_frame, body = channel.basic_get(self._config['queue'])
            if method_frame:
                channel.basic_ack(method_frame.delivery_tag)
                return body
            else:
                return None
        except AMQPConnectionError as e:
            LOGGER.error('connection mq failed!')
