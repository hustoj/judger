import logging
import time

import docker
from docker.errors import NotFound
from requests.exceptions import ConnectionError

LOGGER = logging.getLogger(__name__)


class DockerExecutor(object):
    dir_of_log = ''
    image_name = ''
    command_name = None
    _working_dir = ''
    status = ...
    stdout = ''
    stderr = ''
    sandbox = ''
    time_limit = 30  # base max time limit
    base_url = ''
    sleep_seconds = 30  # sleep when docker connection failed

    def __init__(self) -> None:
        super().__init__()
        self._working_dir = '/data'
        self.base_url = 'unix://var/run/docker.sock'
        self.container_ids = []

    def execute(self, work_dir):
        # type: (str) -> None
        self.sandbox = work_dir
        LOGGER.debug("({image}) running [{command}] in {dir}".format(image=self.image, command=self.command(),
                                                                     dir=self.working_dir))
        retries = 0
        while True:
            if retries > 3:
                raise RuntimeError('Docker has exception')
            try:
                self.do_execute()
                return
            except ConnectionError as e:
                LOGGER.error('docker running timeout !! %s', e)
                retries += 1
                LOGGER.info('retry %d, wait %ds for docker rest', retries, self.sleep_seconds)
                time.sleep(self.sleep_seconds)

    def do_execute(self):
        # client = docker.from_env()
        client = docker.DockerClient(base_url=self.base_url)
        # clean
        client.containers.prune()
        for cid in self.container_ids:
            try:
                c = client.containers.get(cid)
                c.kill()
            except NotFound as e:
                pass
            self.container_ids.remove(cid)

        # start work
        container = client.containers.run(self.image, self.command(), auto_remove=False,
                                          network_disabled=True, detach=True,
                                          read_only=True, volumes=self.volumes(),
                                          working_dir=self.working_dir
                                          )
        container_id = container.id
        self.container_ids.append(container_id)

        self.status = container.wait(timeout=self.time_limit)
        self.stdout = container.logs(stdout=True, stderr=False)
        self.stderr = container.logs(stdout=False, stderr=True)

        # cleanup
        container.remove()
        self.container_ids.remove(container_id)
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
