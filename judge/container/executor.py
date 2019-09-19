import logging

import docker

LOGGER = logging.getLogger(__name__)


class DockerExecutor(object):
    task = ...
    dir_of_log = ''
    image_name = ''
    command_name = None
    _working_dir = ''
    status = ...
    stdout = ''
    stderr = ''
    sandbox = ''
    container = ...  # type: docker.api.APIClient

    def __init__(self) -> None:
        super().__init__()
        self._working_dir = '/data'

    def execute(self, work_dir):
        # type: (str) -> None
        self.sandbox = work_dir
        # client = docker.from_env()
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        LOGGER.debug("({image}) running [{command}] in {dir}".format(image=self.image, command=self.command(),
                                                                     dir=self.working_dir))
        self.container = client.containers.run(self.image, self.command(), auto_remove=False,
                                               network_disabled=True, detach=True,
                                               read_only=True, volumes=self.volumes(),
                                               working_dir=self.working_dir
                                               )
        self.status = self.container.wait()
        self.stdout = self.container.logs(stdout=True, stderr=False)
        self.stderr = self.container.logs(stdout=False, stderr=True)
        self.container.remove()
        client.close()

    def is_ok(self):
        return self.get_status() == 0

    def get_status(self):
        return self.status['StatusCode']

    def get_stdout(self):
        return self.stdout

    def get_stderr(self):
        return self.stderr

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
        self.command_name = name

    def set_image(self, name):
        # type: (str) -> None
        self.image_name = name

    def command(self):
        return self.command_name

    @property
    def image(self):
        return self.image_name

    @property
    def working_dir(self):
        return self._working_dir

    def log_dir(self):
        return self.dir_of_log or '/tmp/runner/'
