#!/bin/env python3

from judge.container import DockerExecutor


class Compiler(DockerExecutor):

    def __init__(self) -> None:
        super().__init__()
        self._image_name = 'compiler:v1'
        self._command_name = 'compiler'
