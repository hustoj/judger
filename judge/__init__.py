#!/bin/env python
# coding: utf8
from time import sleep, time

from judge.config import Config
from judge.data import TaskData, new_data_manager
from judge.language import load_languages
from judge.libs.graceful import GracefulKiller
from judge.remote import new_api
from judge.task import TaskCentre, Task
from judge.worker import Worker
from judge.utils.log import logger

logger = logger()


class Judged(object):
    cfg = ...
    duration = 0.2
    idle_from = 0

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.killer = GracefulKiller()
        self.api = new_api(cfg.api)
        self.dataProvider = new_data_manager(cfg.judged['data_cache'], self.api)
        load_languages()

    def run(self):
        dispatcher = TaskCentre(self.cfg.message_queue)

        while not self.should_stop():
            self.idle_mark()
            job = dispatcher.get_job()
            if job:
                logger.info("New task arrive: {job}".format(job=job))

                worker = Worker(self.cfg, self.api)
                task = Task.from_json(job)
                worker.process(task, self.get_data_provider(task.problem_id))
            else:
                self.take_rest()

    def should_stop(self):
        return self.killer.stop

    def idle_mark(self):
        self.idle_from = time()

    def take_rest(self):
        current = time()
        if self.idle_from < current - 10:
            self.idle_from = current
            logger.info("Task queue empty, heartbeat {duration}s".format(duration=10))

        sleep(self.duration)

    def get_data_provider(self, pid):
        data = self.dataProvider.get_data(pid)
        return TaskData(data)
