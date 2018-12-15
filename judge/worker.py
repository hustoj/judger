#!/bin/env python
# coding: utf8

from .comparer import Compare
from .compiler import Compiler, CompileException
from .constant import Status
from .datautils import DataManager
from .enviro import Environment
from .remote import WebApi
from .result import Result, MAX_USER_OUT
from .runner import get_executor
from .runner.exceptions import ExecuteException, TimeLimitException
from .task import Task
from .log import get_logger


class ResultFiles(object):
    def get_user_out(self):
        return self.read_file('user.out')

    def get_error(self):
        return self.read_file('user.err')

    @staticmethod
    def read_file(name):
        with open(name) as f:
            content = f.read(MAX_USER_OUT)
        return content


class Worker(object):
    data_provider: DataManager
    task: Task
    reporter: WebApi
    cfg = ...
    environ = ...  # type: Environment
    result = ...  # type: Result
    files = ...  # type: ResultFiles
    input_data = ...
    output_data = ...

    def __init__(self, cfg) -> None:
        super().__init__()
        self.cfg = cfg
        self.environ = None

    def set_reporter(self, api: WebApi):
        self.reporter = api

    def process(self, task: Task):
        self.task = task
        self.result = Result.make(Status.ACCEPTED, task.task_id)

        try:
            self._prepare()
            self._compile()
            self._running()
        except CompileException as e:
            get_logger().warning('Task {id} Compile failed: {e}'.format(id=self.task.task_id, e=e))
            self._report(Status.COMPILE_ERROR)
        except TimeLimitException:
            get_logger().error('Task {id} time limit in runner!!'.format(id=self.task.task_id))
            self._report(Status.TIME_LIMIT)
        except ExecuteException as e:
            get_logger().error('Task {id} Execute failed: {e}'.format(id=self.task.task_id, e=e))
            self._report(Status.RUNTIME_ERROR)
        except RuntimeError as e:
            get_logger().error('Catch Runtime Error: %s', e)
        finally:
            self.environ.clean()

    def _running(self):
        total = len(self.input_data)
        current = 1
        for case_id in self.input_data:
            get_logger().info('Task %d, %d cases, current %d', self.task.task_id, total, current)

            self.environ.place_user_input(self.input_data[case_id])

            ret = self._execute()

            get_logger().info('Task %d, Execute result: %s', self.task.task_id, ret)
            if ret is None:
                get_logger().warning('Task %d, Execute result is None', self.task.task_id)
                self.result.result = Status.RUNTIME_ERROR
                break

            case_result = Result()
            case_result.parse_executor_output(ret)

            if case_result.is_accept():
                case_result.result = self._compare_user_answer(self.output_data[case_id])

            self.update_result(case_result)

            if not case_result.is_accept():
                break

            self.environ.prepare_for_next()
            current += 1

        self._report(self.result)

    def update_result(self, case_result):
        # type: (Result) -> None
        if not case_result.is_accept():
            self.result.result = case_result.result
            return
        if case_result.memory_cost > self.result.memory_cost:
            self.result.memory_cost = case_result.memory_cost
        self.result.time_cost += case_result.time_cost

    def _compile(self):
        get_logger().info('Compiling task {id}'.format(id=self.task.task_id))

        self._report(Status.COMPILING)
        compiler = Compiler()
        compiler.compile(self.task.code, self.task.language_type)

    def _execute(self):
        get_logger().info('Executing {id} @ {path}'.format(id=self.task.task_id, path=self.environ.path))
        executor = get_executor()
        return executor.execute(self.task, self.environ.path)

    def _compare_user_answer(self, standard):
        comparator = Compare()
        self.files = ResultFiles()

        return comparator.compare(standard, self.files.get_user_out())

    def _report(self, result):
        if not isinstance(result, Result):
            result = Result.make(result, self.task.task_id)
        self.reporter.report(result)

    def _prepare(self):
        get_logger().info('Prepare environment for task %d', self.task.task_id)

        self.environ = Environment(self.task)

    def set_data_case(self, cases):
        self.input_data = cases['input']
        self.output_data = cases['output']
