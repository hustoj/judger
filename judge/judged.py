#!/bin/env python
# coding: utf8
from time import sleep, time

from .config import Config
from .datautils import new_data_manager
from .graceful import GracefulKiller
from .language import get_language_manager
from .log import get_logger
from .remote import new_api
from .task import TaskCentre, Task
from .worker import Worker

logger = get_logger()


class Judged(object):
    cfg = ...
    duration = 0.2
    idle_from = 0

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.killer = GracefulKiller()
        self.taskCenter = TaskCentre(cfg.message_queue)
        self.langCentre = get_language_manager()
        self.api = new_api(cfg.api)
        self.data_provider = new_data_manager(cfg.judged['data_cache'])
        self.data_provider.set_remote(self.api)

    def run(self):
        self.idle_mark()
        while True:
            if self.killer.should_stop:
                break

            job = self.taskCenter.next_job()
            if job:
                logger.info("New task arrive: {job}".format(job=job))
                task = Task.from_json(job)
                task.set_language(self.get_language(task.language))
                self.process_task(task)
                self.idle_mark()
            else:
                self.take_rest()

    def get_language(self, language):
        return self.langCentre.get_language(language)

    def idle_mark(self):
        self.idle_from = time()

    def take_rest(self):
        current = time()
        if self.idle_from < current - 10:
            self.idle_from = current
            logger.info("Task queue empty, heartbeat {duration}s".format(duration=10))

        sleep(self.duration)

    def process_task(self, task):
        worker = self.get_worker()
        worker.set_data_case(self.get_data(task.problem_id))
        worker.process(task)

    def get_worker(self):
        worker = Worker(self.cfg)
        worker.set_reporter(self.api)

        return worker

    def get_data(self, problem_id):
        return self.data_provider.get_data(problem_id)
