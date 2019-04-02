from judge.container import DockerExecutor


class Runner(DockerExecutor):

    def __init__(self) -> None:
        super().__init__()
        self._image_name = 'runner:v1'
        self._command_name = 'runner'
