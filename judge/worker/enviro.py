import json
import os
import shutil
from tempfile import mkdtemp

from judge.runner import CaseConfig
from judge.utils import is_debug
from judge.utils.log import logger


class Environment(object):
    data_path: str
    task = None
    path = None
    _current_dir = None

    def __init__(self, task):
        self.task = task
        self._current_dir = os.getcwd()
        self._prepare_working_dir()
        self._write_code()
        self.write_case_config()

    def _prepare_working_dir(self):
        self.path = mkdtemp(prefix='judge_')

        logger().info('Task {sid} dir is {path}'.format(sid=self.task.task_id, path=self.path))

        os.chdir(self.path)

    def _write_code(self):
        with open(self.task.language_type.source_name, 'w') as f:
            f.write(self.task.code)

    def place_input(self, data):
        # type: (str) -> None
        with open('user.in', 'w+') as f:
            f.write(data)

    def write_compile_config(self):
        with open('compile.json', 'w+') as f:
            content = json.dumps(self.task.language_type.to_compile_info())
            f.write(content)

    def write_case_config(self):
        config = CaseConfig(self.task)
        config.write_to_file()

    def prepare_for_next(self):
        logger().info("Clear working dir for next case")
        files = ['user.in', 'user.out', 'user.err']
        for file in files:
            if os.path.exists(file):
                os.unlink(file)

    def clean(self):
        if self.path and not is_debug():
            logger().info("Clean working dir {path}".format(path=self.path))
            if os.path.exists(self.path):
                shutil.rmtree(self.path)
            else:
                logger().warning("path is not exist!")
        self.restore()

    def restore(self):
        os.chdir(self._current_dir)
