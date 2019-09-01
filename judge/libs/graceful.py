import logging
import signal

LOGGER = logging.getLogger(__name__)


class GracefulKiller:
    stop = False

    def __init__(self):
        LOGGER.info('Signal register...')
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        LOGGER.info('Judged receive signal, graceful exit...')
        self.stop = True

    @property
    def should_stop(self):
        return self.stop
