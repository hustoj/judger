#!/bin/env python
# coding: utf8
import logging
from time import sleep

from judge.config import Config
from judge.data import new_data_store, InvalidDataCase
from judge.language import load_languages
from judge.libs.graceful import GracefulKiller
from judge.remote import new_api
from judge.task import Task, TaskCentre
from judge.worker import Worker
from judge.utils import JudgeException

LOGGER = logging.getLogger(__name__)


class Judged(object):
    cfg = ...
    duration = 2

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.duration = cfg.judged['sleep_time']
        self.cron = GracefulKiller()
        self.api = new_api(cfg.api)
        self.dataProvider = new_data_store(cfg.judged['data_cache'], self.api)
        load_languages()

    def run(self):
        dispatcher = TaskCentre(self.cfg.message_queue)

        while not self.cron.stop:
            job = dispatcher.get_job()
            if job:
                LOGGER.info("New task arrive: {job}".format(job=job))
                self.handle(job)
            else:
                self.take_rest()
                continue

    def handle(self, job):
        try:
            worker = Worker()
            task = Task.from_json(job)
            if task.language_type.language_id == 3:
                LOGGER.info('java current is not support now')
                return
            if task.is_special:
                LOGGER.info('special judge is not support now')
                return
            worker.process(task, self.dataProvider.get_data(task.problem_id))
            result = worker.get_result()
            self.api.report(result)
        except JudgeException as e:
            LOGGER.error("task failed! {job}: {err}".format(job=job, err=e))

    def take_rest(self):
        LOGGER.info("Task queue empty, idle {duration}s".format(duration=self.duration))
        sleep(self.duration)
