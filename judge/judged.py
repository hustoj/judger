#!/bin/env python
# coding: utf8
from time import sleep, time

from .config import Config
from .datautils import new_data_manager
from .graceful import GracefulKiller
from .language import get_language_manager
from .remote import new_api
from .task import TaskCentre, Task
from .worker import Worker
from .log import get_logger


class Judged(object):
    cfg = ...
    duration = 0.2
    sleep_from = 0

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.killer = GracefulKiller()
        self.taskCenter = TaskCentre(cfg.message_queue)
        self.langCentre = get_language_manager()
        self.api = new_api(cfg.api)
        self.data_provider = new_data_manager(cfg.judged['data_cache'])
        self.data_provider.set_remote(self.api)

    def run(self):
        self.sleep_from = time()
        while True:
            if self.killer.stop:
                break

            job = self.taskCenter.next_job()
            if job:
                get_logger().info("New task arrive: {job}".format(job=job))
                self.run_job(job)
                self.sleep_from = time()
            else:
                self.have_a_rest()

    def have_a_rest(self):
        current = time()
        if self.sleep_from < current - 10:
            self.sleep_from = current
            get_logger().info("Task queue empty, heartbeat {duration}s".format(duration=10))

        sleep(self.duration)

    def run_job(self, job):
        task = Task.from_json(job)
        task.set_language(self.langCentre.get_language(task.language))

        worker = self.get_worker()
        worker.set_data_case(self.data_provider.get_data(task.problem_id))
        worker.process(task)

    def get_worker(self):
        worker = Worker(self.cfg)
        worker.set_reporter(self.api)

        return worker
