#!/bin/env python3

import docker

from judge.task import Task


class DockerExecutor(object):
    def execute(self, task: Task):
        client = docker.from_env()
        client.containers.run("ubuntu", "echo hello world")
