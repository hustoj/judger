import json
import logging
import os
from tempfile import mkdtemp

from judge.utils import write_file
from judge.utils import is_debug

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

    def __init__(self, task):
        """
        :type task: judge.Task
        """
        self.task = task

        self.backup()
        self.path = self.prepare_working_dir()
        LOGGER.info('Task {sid} dir is {path}'.format(sid=task.task_id, path=self.path))

        self.write_code(task.language_type.source_name, task.code)
        self.write_case_info()
        self.write_compile_config()

    def prepare_working_dir(self):
        path = mkdtemp(prefix='judge_')
        os.chdir(path)

        return path

    def write_code(self, filename, code):
        write_file(filename, code)

    def place_input(self, data):
        # type: (str) -> None
        write_file('user.in', data)

    def write_case_info(self):
        cc = CaseConfig(self.task)
        with open('case.json', "w") as f:
            content = json.dumps(cc.to_json())
            f.write(content)

    def write_compile_config(self):
        content = json.dumps(self.task.language_type.to_compile_info())
        write_file('compile.json', content)

    def prepare_for_next(self):
        LOGGER.info("Clear working dir for next case")
        files = ['user.in', 'user.out', 'user.err']
        for file in files:
            if os.path.exists(file):
                os.unlink(file)

    def clean(self):
        pass
        # if self.path and not is_debug():
        #     LOGGER.info("Clean working dir {path}".format(path=self.path))
        #     if os.path.exists(self.path):
        #         shutil.rmtree(self.path)
        #     else:
        #         LOGGER.warning("path is not exist!")
        # self.restore()

    def restore(self):
        os.chdir(self.current_dir)

    def backup(self):
        self.current_dir = os.getcwd()
