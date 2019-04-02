#!/bin/env python
# coding: utf8

from judge.compiler import CompileException, CompilerMaster
from judge.constant import Status
from judge.data import TaskData
from judge.data.manager import DataManager
from judge.log import get_logger
from judge.remote import WebApi
from judge.runner import CaseResult
from judge.runner.exec import Execution
from judge.task import Task
from judge.worker.comparer import Compare
from judge.worker.enviro import Environment
from judge.worker.exceptions import TimeLimitException, ExecuteException
from judge.worker.result import ResultFiles


class Worker(object):
    data_provider: DataManager
    task: Task
    reporter: WebApi
    cfg = ...
    result = None  # type: CaseResult
    cases = None  # type: TaskData

    def __init__(self, cfg, api: WebApi) -> None:
        super().__init__()
        self.cfg = cfg
        self.reporter = api

    def process(self, task: Task, data: TaskData):
        self.task = task
        self.cases = data
        self.result = CaseResult.make(Status.ACCEPTED, task.task_id)

        try:
            sandbox = self.prepare()
            self.task.working_dir = sandbox.path
            self.compile(sandbox)
            self.running(sandbox)
            sandbox.clean()
        except CompileException as e:
            get_logger().warning('Task {id} Compile failed: {e}'.format(id=self.task.task_id, e=e))
            self.report_status(Status.COMPILE_ERROR)
        except TimeLimitException:
            get_logger().error('Task {id} time limit in runner!!'.format(id=self.task.task_id))
            self.report_status(Status.TIME_LIMIT)
        except ExecuteException as e:
            get_logger().error('Task {id} Execute failed: {e}'.format(id=self.task.task_id, e=e))
            self.report_status(Status.RUNTIME_ERROR)
        except RuntimeError as e:
            get_logger().error('Catch Runtime Error: %s', e)

    def execute(self, sandbox: Environment, index):
        standard_input = self.cases.get_input(index)
        standard_output = self.cases.get_output(index)
        try:
            execution = Execution(sandbox)
            case_result = execution.execute(self.task, standard_input)
            get_logger().info('Task %d, case %d Execute success', self.task.task_id, index)

            if case_result.is_ok():
                case_result.result = ResultFiles.compare_output(standard_output)

            return case_result
        except ExecuteException as e:
            get_logger().error('Task %d, case %d failed: code: %d, out: %s, err: %s.',
                               self.task.task_id, index, e.code, e.user_out, e.user_err)

    def running(self, sandbox: Environment):
        get_logger().info('Executing {id} @ {path}'.format(id=self.task.task_id, path=sandbox.path))

        total = self.cases.count

        for index in range(0, total):
            get_logger().info('Task %d, case %d, total %d', self.task.task_id, index, total)
            case_result = self.execute(sandbox, index)
            self.result.update_by_case(case_result)
            if not self.result.is_ok():
                break

        # report final result
        self.reporter.report(self.result)

    def compile(self, sandbox):
        get_logger().info('Compiling task {id}'.format(id=self.task.task_id))
        sandbox.write_compile_config()

        self.report_status(Status.COMPILING)
        compiler = CompilerMaster()
        return compiler.compile(self.task)

    def report_status(self, status):
        final_result = CaseResult.make(status, self.task.task_id)
        self.reporter.report(final_result)

    def prepare(self) -> Environment:
        get_logger().info('Prepare environment for task %d', self.task.task_id)

        environ = Environment(self.task)
        return environ
