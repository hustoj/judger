from docker.errors import DockerException

from judge.container.runner import Runner
from judge.log import get_logger
from judge.runner.result import CaseResult
from judge.worker.enviro import Environment
from judge.worker.exceptions import ExecuteException


class Execution(object):
    def __init__(self, sandbox: Environment):
        self.sandbox = sandbox

    def execute(self, task, standard_input):
        self.sandbox.prepare_for_next()
        self.sandbox.place_input(standard_input)

        try:
            runner = Runner()
            runner.execute(task)
            get_logger().info('Executor: Task %d finished, result: %s', task.task_id, runner.get_status())
            if not runner.is_ok():
                raise ExecuteException(runner.get_status(), runner.get_stdout(), runner.get_stderr())

            return CaseResult.parse_runner(runner.get_stdout())
        except DockerException as err:
            get_logger().error('Docker Exception:', err)
            exit(1)
