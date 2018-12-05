import json
import logging
import os
import shutil
from tempfile import mkdtemp

from judge.utils import is_debug


class Environment(object):
    data_path: str
    task = None
    path = None
    _current_dir = None

    def __init__(self, task):
        self.task = task
        self._current_dir = os.getcwd()
        self._prepare_working_dir()
        self.write_case_config()

    def _prepare_working_dir(self):
        self.path = mkdtemp(prefix='judge_')

        logging.info('Task {sid} dir is {path}'.format(sid=self.task.task_id, path=self.path))

        os.chdir(self.path)

    def place_user_input(self, data):
        # type: (str) -> None
        inf = open('user.in', 'w+')
        inf.write(data)
        inf.close()

    def write_case_config(self):
        file = open("case.conf", "w")
        content = json.dumps(self.task.as_task_info())
        file.write(content)
        file.close()

    def prepare_for_next(self):
        logging.info("Clear working dir for next case")
        files = ['user.in', 'user.out', 'user.err']
        for file in files:
            os.unlink(file)

    def clean(self):
        if self.path and not is_debug():
            logging.info("Clean working dir {path}".format(path=self.path))
            if os.path.exists(self.path):
                shutil.rmtree(self.path)
            else:
                logging.warning("path is not exist!")
        self.restore()

    def restore(self):
        os.chdir(self._current_dir)
