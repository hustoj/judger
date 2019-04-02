import os

from judge.log import get_logger


def get_file_content(path):
    f = open(path)
    data = f.read()
    f.close()
    return data


def write_file(path, content):
    f = open(path, 'w')
    f.write(content)
    f.close()


class LocalCache(object):
    def __init__(self, path) -> None:
        super().__init__()
        self.path = path

    def cached(self, pid):
        if os.path.exists(self._get_data_path(pid)):
            return True
        return False

    def save_data(self, pid, content):
        # type: (int, bytes) -> None
        path = self._get_data_path(pid)
        get_logger().info('write {path} data'.format(path=path))
        write_file(path, content.decode())

    def get_data(self, pid):
        path = self._get_data_path(pid)
        get_logger().info('get data of %d, %s', pid, path)
        return get_file_content(path)

    def _get_data_path(self, pid):
        filename = '{pid}.json'.format(pid=pid)

        return os.path.join(self.path, filename)
