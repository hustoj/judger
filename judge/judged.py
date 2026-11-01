#!/bin/env python
# coding: utf8
import logging
from time import sleep

from judge.config import Config
from judge.data import new_data_provider
from judge.language import load_languages, LanguageType, LANG_JAVA
from judge.libs.graceful import GracefulKiller
from judge.remote import new_api
from judge.task import Task, TaskDispatcher
from judge.utils import JudgeException
from judge.worker import Worker

LOGGER = logging.getLogger(__name__)


class Judged(object):
    _config = ...
    duration = 2

    def __init__(self, cfg: Config):
        self._config = cfg
        self.duration = cfg.judged['idle_time']
        self.signal = GracefulKiller()
        self.api = new_api(cfg.api)
        self.dataProvider = new_data_provider(cfg.judged['data_cache'], self.api)
        load_languages()

    def run(self):
        dispatcher = TaskDispatcher(self._config.message_queue)

        while not self.signal.stop:
            jobs = dispatcher.get_job()
            if len(jobs) == 0:
                self.take_rest()
                continue
            LOGGER.info('Received %d judge task(s)', len(jobs) if isinstance(jobs, list) else 1)
            if isinstance(jobs, list):
                for job in jobs:
                    self.handle(job)
            else:
                self.handle(jobs)

    def handle(self, job):
        task_id = 'unknown'
        try:
            task = Task.from_json(job)
            task_id = task.task_id
            if not isinstance(task.judge_token, str) or not task.judge_token.strip():
                raise JudgeException('Judge task token is missing')
            if not self.is_support(task):
                return
            worker = Worker()
            worker.process(task, self.dataProvider.get_data(task.problem_id))
            result = worker.get_result()
            self.api.report(result, task.judge_token)
        except JudgeException as e:
            LOGGER.error('Task %s failed: %s', task_id, e)

    def is_support(self, task: Task):
        if task.is_special:
            LOGGER.info('{} is special judge, current not support now'.format(task.task_id))
            return False
        if not task.language_type.is_enabled:
            LOGGER.info('language {} current is not support now'.format(task.language_type))
            return False
        return True

    def take_rest(self):
        sleep(self.duration)
