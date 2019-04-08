import signal

from judge.utils.log import logger


class GracefulKiller:
    stop = False

    def __init__(self):
        logger().info('Signal register...')
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logger().info('Judged receive signal, graceful exit...')
        self.stop = True

    @property
    def should_stop(self):
        return self.stop
