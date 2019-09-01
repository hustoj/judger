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

LOGGER = logging.getLogger(__name__)


class Judged(object):
    cfg = ...
    duration = 2

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.killer = GracefulKiller()
        self.api = new_api(cfg.api)
        self.dataProvider = new_data_store(cfg.judged['data_cache'], self.api)
        load_languages()

    def run(self):
        dispatcher = TaskCentre(self.cfg.message_queue)

        while self.go():
            job = dispatcher.get_job()
            if job:
                self.handle(job)
            else:
                self.take_rest()

    def handle(self, job):
        LOGGER.info("New task arrive: {job}".format(job=job))
        worker = Worker()
        task = Task.from_json(job)
        try:
            worker.process(task, self.dataProvider.get_data(task.problem_id))
            result = worker.get_result()
            self.api.report(result)
        except InvalidDataCase as e:
            LOGGER.error("task data invalid! {task_id}".format(task_id=task.task_id))

    def go(self):
        return not self.killer.stop

    def take_rest(self):
        LOGGER.info("Task queue empty, idle {duration}s".format(duration=self.duration))
        sleep(self.duration)
