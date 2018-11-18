import logging
import os
import shutil
import json
from tempfile import mkdtemp

from judge.datautils import DataManager
from judge.utils import is_debug


class Environment(object):
    data_path: str
    provider: DataManager
    task = None
    path = None
    _current_dir = None

    def prepare(self, task):
        self.task = task
        self._current_dir = os.getcwd()
        self._prepare_working_dir()
        self._place_user_input()
        # self.write_case_config()

    def _prepare_working_dir(self):
        self.path = mkdtemp(prefix='judge_')

        logging.info('worker {pid} dir is {path}'.format(pid=self.task.problem_id, path=self.path))

        os.chdir(self.path)

    def _place_user_input(self):
        data = self.provider.get_input(self.task.problem_id)
        inf = open('data.in', 'w+')
        inf.write(data)
        inf.close()

    def write_case_config(self):
        file = open("case.conf", "w")
        task_info = self.task.as_task_info()
        content = json.dumps(task_info)
        file.write(content)
        file.close()

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

    def set_data_provider(self, provider):
        self.provider = provider
