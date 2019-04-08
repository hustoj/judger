import os
import time

import psutil


class PIDFile(object):
    __slots__ = ('__file', '__checked', '__process')

    def __init__(self, pid_file):
        self.__file = pid_file
        self.__checked = None
        self.__process = psutil.Process(os.getppid())

    def check_process_cmd_line(self, pid):
        try:
            cmd1 = psutil.Process(pid).cmdline()[:1]
            cmd2 = self.__process.cmdline()[:1]
            return cmd1 == cmd2
        except psutil.AccessDenied:
            return False

    def check_pid_is_running(self):
        """
        Returns `True` if process which created pid-file is
        already dead or has different script name.

        :return: bool
        """
        if not os.path.exists(self.__file):
            return True

        with open(self.__file, "r") as f:
            try:
                pid = int(f.read().strip())
            except Exception:
                return True

        for p in psutil.pids():
            if p == pid:
                return self.check_process_cmd_line(pid)

        return True

    def __enter__(self):
        result = self.check_pid_is_running()

        if not result:
            raise RuntimeError("Program already running.")

        with open(self.__file, "w+") as f:
            f.write(str(os.getpid()))
            f.flush()

    def __exit__(self, *args):
        if self.__checked and os.path.exists(self.__file):
            try:
                os.unlink(self.__file)
            except Exception:
                pass


if __name__ == '__main__':
    pid_path = '/tmp/test.pid'
    with PIDFile(pid_path):
        time.sleep(30)
