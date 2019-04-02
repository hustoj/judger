import signal

from judge.log import get_logger


class GracefulKiller:
    stop = False

    def __init__(self):
        get_logger().info('Signal register...')
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        get_logger().info('Judged receive signal, graceful exit...')
        self.stop = True

    @property
    def should_stop(self):
        return self.stop
