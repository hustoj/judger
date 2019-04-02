#!/bin/env python3

import docker
from docker.models.containers import Container

from judge.task import Task


class DockerExecutor(object):
    task = ...
    dir_of_log = ''
    _image_name = ''
    _command_name = ''
    _working_dir = ''
    status = ...
    stdout = ''
    stderr = ''
    container = ...  # type: Container

    def __init__(self) -> None:
        super().__init__()
        self._working_dir = '/data'

    def execute(self, task):
        # type: (Task) -> None
        self.task = task
        client = docker.from_env()
        self.container = client.containers.run(self.image, self.command(), auto_remove=True,
                                               network_disabled=True, detach=True,
                                               read_only=True, volumes=self.volumes(),
                                               working_dir=self.working_dir
                                               )
        self.stdout = self.container.logs(stdout=True, stderr=False)
        self.stderr = self.container.logs(stdout=False, stderr=True)
        self.status = self.container.wait()
        client.close()

    def is_ok(self):
        return self.get_status() == 0

    def get_status(self):
        return self.status['StatusCode']

    def get_stdout(self):
        return self.stdout

    def get_stderr(self):
        return self.stderr

    @property
    def sandbox(self):
        """
        get outer working sandbox dir
        :return: str
        """
        return self.task.working_dir

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

    def set_command(self, name):
        # type: (str) -> None
        self._command_name = name

    def set_image(self, name):
        # type: (str) -> None
        self._image_name = name

    def command(self):
        return self._command_name

    @property
    def image(self):
        return self._image_name

    @property
    def working_dir(self):
        return self._working_dir

    def log_dir(self):
        return self.dir_of_log or '/tmp/runner/'
