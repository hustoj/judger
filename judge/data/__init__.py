from .cache import LocalCache
from .manager import DataManager


class TaskData(object):
    total = 0

    def __init__(self, cases):
        self.cases = cases
        self.validate()

    def validate(self):
        if 'input' not in self.cases or 'output' not in self.cases:
            return False

        if self.count != len(self.cases['output']):
            return False

        self.total = len(self.cases['input'])
        return True

    @property
    def count(self):
        return self.total

    def get_input(self, index):
        if index > self.total:
            return None
        return self.cases['input'][index]

    def get_output(self, index):
        if index > self.total:
            return None
        return self.cases['output'][index]


def new_data_manager(path, api) -> DataManager:
    manager = DataManager()
    manager.set_cache(LocalCache(path))
    manager.set_remote(api)

    return manager
