#!/bin/env python
# coding: utf8

import fcntl
import os
import signal
import sys
from time import sleep

from peewee import DoesNotExist

from db import get_job
from utils import cfg, logger
from worker import Worker, WorkerIsBusy


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logger.info('receive signal, exiting')
        self.kill_now = True


class Daemon(object):
    _worker = {}
    _maxWorker = 8

    def __init__(self, worker_limit=10):
        super(Daemon, self).__init__()
        self._maxWorker = worker_limit + 1
        for i in range(1, self._maxWorker):
            self._worker[i] = 1

    def get_worker(self):
        """
            :rtype: worker.Worker
        """
        for i in range(1, self._maxWorker):
            if isinstance(self._worker[i], Worker):
                continue
            self._worker[i] = Worker(i)
            return self._worker[i]
        raise WorkerIsBusy

    def clean_files(self):
        os.remove(cfg.server.pid_file)

    def run(self):
        self.singleton()
        killer = GracefulKiller()
        while True:
            if killer.kill_now:
                break
            try:
                job = get_job()
                worker = self.get_worker()
                worker.process(job)
            except DoesNotExist as e:
                logger.info('no job available, sleeping')
                sleep(3)
            except WorkerIsBusy as e:
                logger.info('no worker available, sleeping')
                sleep(3)

    def __del__(self):
        self.clean_files()

    def singleton(self):
        fp = open(cfg.server.pid_file, 'w')
        try:
            fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fp.write('{pid}\n'.format(pid=os.getpid()))
        except IOError as e:
            print('other instance is running, exit')
            sys.exit(0)


if __name__ == '__main__':
    judger = Daemon()
    judger.run()
