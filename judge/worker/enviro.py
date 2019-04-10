import json
import os
import shutil
from tempfile import mkdtemp

from judge.runner import CaseConfig
from judge.utils import is_debug, write_file
from judge.utils.log import logger


class Environment(object):
    data_path: str
    task = None
    path = None
    current_dir = None

    def __init__(self, task):
        self.task = task

        self.backup()
        self.path = self.prepare_working_dir()
        logger().info('Task {sid} dir is {path}'.format(sid=task.task_id, path=self.path))

        self.write_code(task.language_type.source_name, task.code)

        # write config
        CaseConfig(task).write_to_file()

    def prepare_working_dir(self):
        path = mkdtemp(prefix='judge_')
        os.chdir(path)

        return path

    def write_code(self, filename, code):
        write_file(filename, code)

    def place_input(self, data):
        # type: (str) -> None
        write_file('user.in', data)

    def write_compile_config(self):
        content = json.dumps(self.task.language_type.to_compile_info())
        write_file('compile.json', content)

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
        os.chdir(self.current_dir)

    def backup(self):
        self.current_dir = os.getcwd()
