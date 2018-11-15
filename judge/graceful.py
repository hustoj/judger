import logging
import signal


class GracefulKiller:
    stop = False

    def __init__(self):
        logging.info('Signal register...')
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logging.info('Judged receive signal, graceful exit...')
        self.stop = True
