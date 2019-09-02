import json
import logging
import os
import shutil
from tempfile import mkdtemp

from judge.utils import is_debug
from judge.utils import write_file

LOGGER = logging.getLogger(__name__)


class CaseConfig(object):
    def __init__(self, task):
        self.task = task

    def to_json(self):
        return {
            'cpu': self.task.time_limit,
            'memory': self.task.memory_limit,
            'language': self.task.language,
            'output': self.task.output_limit,
            'verbose': is_debug(),
        }


class Environment(object):
    data_path: str
    current_dir = None
    path: str

    def __init__(self, task):
        """
        :type task: judge.task.Task
        """
        self.task = task

        self.backup()
        self.make_work_dir()
        self.prepare_compile()
        self.write_case_info()

    def make_work_dir(self):
        self.path = mkdtemp(prefix='judge_')
        os.chdir(self.path)
        LOGGER.info('Task {sid} dir is {path}'.format(sid=self.task.task_id, path=self.path))

    def place_input(self, data):
        # type: (str) -> None
        write_file('user.in', data)

    def write_case_info(self):
        cc = CaseConfig(self.task)
        with open('case.json', "w") as f:
            content = json.dumps(cc.to_json())
            f.write(content)

    def prepare_compile(self):
        write_file(self.task.language_type.source_name, self.task.code)
        content = json.dumps(self.task.language_type.to_compile_info())
        write_file('compile.json', content)

    def clear_user_data(self):
        LOGGER.info("Clear working dir for next case")
        files = ['user.in', 'user.out', 'user.err']
        for file in files:
            if os.path.exists(file):
                os.unlink(file)

    def clean(self):
        if self.path and not is_debug():
            LOGGER.info("Clean working dir {path}".format(path=self.path))
            if os.path.exists(self.path):
                shutil.rmtree(self.path)
            else:
                LOGGER.error("working path[{path}] is not exist!".format(path=self.path))
        self.restore()

    def restore(self):
        os.chdir(self.current_dir)

    def backup(self):
        self.current_dir = os.getcwd()
