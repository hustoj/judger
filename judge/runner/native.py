import logging
import subprocess
from signal import alarm, signal, SIGALRM

from runner import alarm_handler, ExecuteException, Alarm, TimeLimitException
from judge.task import Task

MAX_USER_OUT = 65536


class NativeExecutor(object):
    def execute(self, task: Task):
        args = task.running_command
        indata = open("data.in")
        userout = open("user.out", "w")
        p = subprocess.Popen(args, shell=False, stdin=indata, stdout=userout, stderr=subprocess.PIPE,
                             universal_newlines=True)
        signal(SIGALRM, alarm_handler)
        alarm(task.time_limit * 5)
        try:
            (stdoutData, stderrData) = p.communicate()
            if stderrData or stdoutData:
                logging.warning("Executor error: \nout:\n---\n%s\n---\nerr:\n---\n%s\n---", stdoutData, stderrData)
            if p.returncode != 0:
                raise ExecuteException(str(stderrData, 'utf8'))
            alarm(0)  # cancel any alarm
            logging.info('Task {id} execute finished!'.format(id=self.task.task_id))
            if stdoutData is None:
                return ''
            return stdoutData
        except Alarm as e:
            logging.error('Alarm Signal received %d')
            p.kill()
            raise TimeLimitException('Time out')
