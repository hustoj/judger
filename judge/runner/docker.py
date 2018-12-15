#!/bin/env python3

import docker

from docker.errors import ContainerError
from judge.task import Task
from judge.log import get_logger


class DockerExecutor(object):
    task = ''
    sandbox = ''
    dir_of_log = ''
    _image_name = ''
    _command_name = ''

    def execute(self, task, sandbox):
        # type: (Task, str) -> str
        self.task = task
        self.sandbox = sandbox
        try:
            ret = self.do_execute()
            return ret
        except ContainerError as error:
            get_logger().error('Execute Failed: %s', error)

    def volumes(self):
        return {
            self.sandbox: {
                'bind': self.working_dir,
                'mode': 'rw'
            },
            self.log_dir(): {
                'bind': '/var/log/runner',
                'mode': 'rw'
            }
        }

    def do_execute(self):
        client = docker.from_env()
        ret = client.containers.run(self.image, self.command(), auto_remove=True,
                                    network_disabled=True,
                                    read_only=True, volumes=self.volumes(),
                                    working_dir=self.working_dir,
                                    # pids_limit=self.pids_limit,
                                    # mem_limit=self.mem_limit, memswap_limit=self.mem_limit,
                                    # cpuset_cpus='1', ulimits=self.ulimits()
                                    )
        client.close()
        get_logger().info('Task %d Docker execute finished, result: %s', self.task.task_id, ret)
        return ret

    def set_command(self, name):
        # type: (str) -> None
        self._command_name = name

    def set_image(self, name):
        # type: (str) -> None
        self._image_name = name

    def ulimits(self):
        return [
            {
                'Name': 'nofile',  # limit create files
                'Soft': 10,
                'Hard': 10,
            }
        ]

    def command(self):
        return self._command_name or 'runner'

    @property
    def image(self):
        return self._image_name or "runner:v1"

    @property
    def working_dir(self):
        return '/home/judger'

    def log_dir(self):
        return self.dir_of_log or '/tmp/runner/'

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
