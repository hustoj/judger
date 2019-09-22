import logging

from docker.errors import DockerException

from judge.result import CaseResult
from .executor import DockerExecutor

LOGGER = logging.getLogger(__name__)


class JudgeException(Exception):
    pass


class ExecuteException(JudgeException):
    def __init__(self, code, user_out, user_err):
        self.code = code
        self.user_out = user_out
        self.user_err = user_err


class TimeLimitException(ExecuteException):
    pass


class Runner(object):
    def execute(self, env, standard_input):
        """
        :param judge.worker.enviro.Environment env:
        :param str standard_input:
        :return:
        """
        env.clear_user_data()
        env.place_input(standard_input)

        try:
            runner = DockerExecutor()
            runner.set_image(env.task.language_type.running_image)
            runner.set_command("runner")
            runner.time_limit = env.task.time_limit * 2
            runner.execute(env.path)
            LOGGER.info('Executor: Task %d finished, result: %s', env.task.task_id, runner.get_status())
            if not runner.is_ok():
                raise ExecuteException(runner.get_status(), runner.get_stdout(), runner.get_stderr())
            # todo: get_stdout() may return b'' cause failed
            return CaseResult.parse_runner(runner.get_stdout())
        except DockerException as err:
            LOGGER.critical('Docker Exception: {err}'.format(err=err.args))
            exit(1)


