import json

from judge.utils import is_debug


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

    def write_to_file(self, name='case.json'):
        with open(name, "w") as f:
            content = json.dumps(self.to_json())
            f.write(content)
