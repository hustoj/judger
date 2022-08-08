import json
import logging

import boto3
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


class RabbitMqProvider(object):
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

    def get_task(self):
        try:
            channel = self._get_connection().channel()
            method_frame, header_frame, body = channel.basic_get(self._config['queue'])
            if method_frame:
                channel.basic_ack(method_frame.delivery_tag)
                return [body]
            else:
                return []
        except AMQPConnectionError as e:
            LOGGER.error('connection mq failed!')

    def delete_task(self, task):
        pass


class SqsProvider(object):
    _client = None
    _config = None
    _queue_url = None

    def __init__(self, config):
        self._config = config
        self._client = boto3.client('sqs', region_name=config['region'])
        self._queue_url = self._config['queue_url']

    def get_task(self):
        response = self._client.receive_message(
            QueueUrl=self._queue_url,
            MaxNumberOfMessages=1
        )
        if 'Messages' not in response:
            LOGGER.info('no task receive from sqs')
            return []
        jobs = []
        for message in response['Messages']:
            jobs.append(message['Body'])
            self.delete_task(message['ReceiptHandle'])
        return jobs

    def delete_task(self, receipt):
        ret = self._client.delete_message(
            QueueUrl=self._queue_url,
            ReceiptHandle=receipt
        )
        LOGGER.info('delete task {} ret: {}'.format(receipt, ret))


class TaskCentre(object):
    _connection = None
    _config = None
    _provider = None

    def __init__(self, config):
        self._config = config
        if 'sqs' == config['driver']:
            self._provider = SqsProvider(config['sqs'])
        if 'rabbitmq' == config['driver']:
            self._provider = RabbitMqProvider(config['rabbitmq'])

    def get_job(self):
        return self._provider.get_task()
