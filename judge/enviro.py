import logging
import os
import shutil
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
        f = open('data.in', 'w+')
        f.write(data)
        f.close()

    def write_case_config(self):
        file = open("case.conf", "w")
        file.write("{0}\n".format(self.task.time_limit))
        file.write("{0}\n".format(self.task.memory_limit))
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
