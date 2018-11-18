#!/bin/env python
# coding: utf8
import logging
from time import sleep

from .config import Config
from .datautils import new_data_manager
from .remote import new_api
from .task import TaskCentre, Task
from .worker import Worker
from .graceful import GracefulKiller
from .language import get_language_manager


class Judged(object):
    cfg = ...
    duration = 3

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.killer = GracefulKiller()
        self.taskCenter = TaskCentre(cfg.message_queue)
        self.languageCentre = get_language_manager()
        self.api = new_api(cfg.api)
        self.data_provider = new_data_manager(cfg.judged['data_cache'])
        self.data_provider.set_provider(self.api)

    def run(self):
        while True:
            if self.killer.stop:
                break
            job = self.taskCenter.next_job()

            if job:
                self._run_job(job)
            else:
                logging.info("no task to execute, sleep {duration}s".format(duration=self.duration))
                sleep(self.duration)

    def _run_job(self, job):
        logging.info("get task {job}".format(job=job))
        task = Task.from_json(job)
        task.set_language(self.get_language(task.language))
        worker = self.get_worker()
        worker.process(task)

    def get_worker(self):
        worker = Worker(self.cfg)
        worker.set_data_provider(self.data_provider)
        worker.set_reporter(self.api)

        return worker

    def get_language(self, language_id):
        return self.languageCentre.get_language(language_id)
