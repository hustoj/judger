#!/bin/env python
# coding: utf8
import logging

from judge.container import CompileException, Compiler
from judge.container import Runner
from judge.container.runner import TimeLimitException, ExecuteException
from judge.data import CaseManager
from judge.result import Status, CaseResult
from judge.task import Task
from .enviro import Environment
from .result import ResultFiles

LOGGER = logging.getLogger(__name__)


class Worker(object):
    task: Task
    result = None  # type: CaseResult
    task_data = None  # type: CaseManager
    sandbox: Environment

    def process(self, task: Task, data: CaseManager):
        self.task = task
        self.task_data = data
        self.result = CaseResult.make(Status.ACCEPTED, task.task_id)

        try:
            self.sandbox = self.prepare()
            self.compile()
            self.running()
            self.sandbox.clean()
        except CompileException as e:
            LOGGER.warning('Task {id} Compile failed: {e}'.format(id=self.task.task_id, e=e))
            self.result.result = Status.COMPILE_ERROR
        except TimeLimitException:
            LOGGER.error('Task {id} time limit in runner!!'.format(id=self.task.task_id))
            self.result.result = Status.TIME_LIMIT
        except ExecuteException as e:
            LOGGER.error('Task {id} Execute failed: {e}'.format(id=self.task.task_id, e=e))
            self.result.result = Status.RUNTIME_ERROR
        except RuntimeError as e:
            LOGGER.error('Catch Runtime Error: %s', e)

    def execute(self, case_item):
        execution = Runner()
        case_result = execution.execute(self.sandbox, case_item['input'])

        if case_result.is_ok():
            case_result.result = ResultFiles.compare_output(case_item['output'])

        return case_result

    def running(self):
        LOGGER.info('Executing {id} @ {path}'.format(id=self.task.task_id, path=self.sandbox.path))

        index = 0
        for dataCase in self.task_data:
            index += 1
            LOGGER.info('Task %d, case %d, total %d', self.task.task_id, index, self.task_data.count)
            try:
                case_result = self.execute(dataCase)
                LOGGER.info('Task %d, case %d Execute finished', self.task.task_id, index)
                self.result.update_by_case(case_result)
                if not self.result.is_ok():
                    break
            except ExecuteException as e:
                LOGGER.error('Task %d, case %d failed: code: %d, out: %s, err: %s.',
                             self.task.task_id, index, e.code, e.user_out, e.user_err)

    def compile(self):
        LOGGER.info('Compiling task {id}'.format(id=self.task.task_id))
        return Compiler.compile(self.sandbox)

    def prepare(self) -> Environment:
        LOGGER.info('Prepare environment for task %d', self.task.task_id)

        environ = Environment(self.task)
        return environ

    def get_result(self):
        return self.result
