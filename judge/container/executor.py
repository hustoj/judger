import logging
import os
import time

import docker
from docker.errors import NotFound
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ReadTimeout

LOGGER = logging.getLogger(__name__)
MAX_DOCKER_RETRIES = 3


class DockerExecutor:
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
    sleep_seconds = 5  # sleep when docker connection failed

    def __init__(self) -> None:
        super().__init__()
        self._working_dir = '/data'
        self.base_url = 'unix:///var/run/docker.sock'
        self.container_ids = []

    def execute(self, work_dir):
        # type: (str) -> None
        self.sandbox = work_dir
        LOGGER.debug(
            "(%s) running [%s] in %s",
            self.image,
            self.command(),
            self.working_dir,
        )
        retries = 0
        while True:
            if retries > MAX_DOCKER_RETRIES:
                raise RuntimeError('Docker has exception')
            try:
                self.do_execute()
                return
            except (RequestsConnectionError, ReadTimeout) as e:
                LOGGER.error('docker running timeout !! %s', e)
                retries += 1
                LOGGER.info('retry %d, wait %ds for docker rest', retries, self.sleep_seconds)
                time.sleep(self.sleep_seconds)

    def do_execute(self):
        # client = docker.from_env()
        client = docker.DockerClient(base_url=self.base_url)
        container = None
        container_id = None
        try:
            # Clean containers left behind by an interrupted Docker API call.
            for cid in list(self.container_ids):
                try:
                    client.containers.get(cid).remove(force=True)
                except NotFound:
                    pass
                self.container_ids.remove(cid)

            container = client.containers.run(
                self.image,
                self.command(),
                auto_remove=False,
                network_disabled=True,
                detach=True,
                read_only=True,
                volumes=self.volumes(),
                working_dir=self.working_dir,
                user='0:0',
                cap_add=['SYS_PTRACE'],
                security_opt=['no-new-privileges:true'],
                environment={
                    'RUNNER_CGROUP_MOUNT': '/run/hustoj-cgroup',
                    'RUNNER_CGROUP_PARENT': '/run/hustoj-cgroup',
                },
            )
            container_id = container.id
            self.container_ids.append(container_id)

            self.status = container.wait(timeout=self.time_limit)
            self.stdout = container.logs(stdout=True, stderr=False)
            self.stderr = container.logs(stdout=False, stderr=True)
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except NotFound:
                    pass
            if container_id in self.container_ids:
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
            },
            os.environ.get('JUDGE_CGROUP_PARENT', '/sys/fs/cgroup/hustoj-judger'): {
                'bind': '/run/hustoj-cgroup',
                'mode': 'rw',
            },
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
