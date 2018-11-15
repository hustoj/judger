import toml


class Config(object):
    _cfg = ...

    def __init__(self, cfg):
        self._cfg = cfg

    @property
    def message_queue(self):
        return self._cfg['mq']

    @property
    def api(self):
        return self._cfg['api']

    @property
    def worker(self):
        return self._cfg['worker']

    @property
    def judged(self):
        return self._cfg['judged']


def load_config(path) -> Config:
    c = toml.load(path)
    return Config(c)
