#!/bin/env python3

import docker
import logging
from docker.errors import ContainerError
from judge.task import Task


class DockerExecutor(object):
    task: Task
    sandbox = ''

    def execute(self, task: Task, sandbox: str):
        self.task = task
        self.sandbox = sandbox
        try:
            ret = self.do_execute()
            return ret
        except ContainerError as error:
            logging.error('Execute Failed: %s', error)

    def volumes(self):
        return {
            self.sandbox: {
                'bind': self.working_dir,
                'mode': 'rw'
            }
        }

    def do_execute(self):
        client = docker.from_env()
        ret = client.containers.run(self.image, self.command(), auto_remove=True,
                                    network_disabled=True,
                                    read_only=True, volumes=self.volumes(),
                                    working_dir=self.working_dir,
                                    pids_limit=self.pids_limit,
                                    mem_limit=self.mem_limit, memswap_limit=self.mem_limit,
                                    cpuset_cpus='1', ulimits=self.ulimits()
                                    )
        logging.info('Task %d Docker execute finished, result: %s', self.task.task_id, ret)
        return ret

    def ulimits(self):
        return [
            {
                'Name': 'nofile',  # limit create files
                'Soft': 10,
                'Hard': 10,
            }
        ]

    def command(self):
        return 'runner'

    @property
    def image(self):
        return "ubuntu:18.04"

    @property
    def working_dir(self):
        return '/home/judger'

    @property
    def mem_limit(self):
        # Unit can be one of b, k, m, or g. Minimum is 4M.
        size = self.task.memory_limit * 2
        if size < 4:
            size = 4
        memory = "{size}m".format(size=size)
        return memory

    @property
    def pids_limit(self):
        return 10
