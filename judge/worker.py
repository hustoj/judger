#!/bin/env python
# coding: utf8

import logging

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


class Worker(object):
    data_provider: DataManager
    task: Task
    reporter: WebApi
    cfg = ...
    environ: Environment
    result: Result

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
            ret = self._execute()
            self._parse_result(ret)
        except CompileException as e:
            logging.warning('{id} Compile failed: {e}'.format(id=self.task.task_id, e=e))
            self._report(Status.COMPILE_ERROR)
        except TimeLimitException:
            logging.error('{id} time limit in runner!!'.format(id=self.task.task_id))
            self._report(Status.TIME_LIMIT)
        except ExecuteException as e:
            logging.error('{id} Execute failed: {e}'.format(id=self.task.task_id, e=e))
            self._report(Status.RUNTIME_ERROR)
        except RuntimeError as e:
            logging.error('Catch Runtime Error: %s', e)
        finally:
            self.environ.clean()

    def _compile(self):
        logging.info('Compiling {id}'.format(id=self.task.task_id))
        self._report(Status.COMPILING)
        compiler = Compiler()
        compiler.compile(self.task.code, self.task.language_type)

    def _execute(self):
        logging.info('Executing {id} @ {path}'.format(id=self.task.task_id, path=self.environ.path))
        executor = get_executor()
        return executor.execute(self.task, self.environ.path)

    def _parse_result(self, content):
        logging.info('%d, Execute result: %s', self.task.task_id, content)
        self.result.parse_executor_output(content)

        if self.result.is_accept():
            self.result.result = self._compare()

        self._report(self.result)

    def _compare(self):
        comparator = Compare()
        with open('user.out') as f:
            user_out = f.read(MAX_USER_OUT)
        standard_data = self.data_provider.get_output(self.task.task_id)
        return comparator.compare(standard_data, user_out)

    def _report(self, result):
        if not isinstance(result, Result):
            result = Result.make(result, self.task.task_id)
        self.reporter.report(result)

    def _prepare(self):
        logging.info('prepare environment, %d', self.task.task_id)

        self.environ = Environment()
        self.environ.set_data_provider(self.data_provider)
        self.environ.prepare(self.task)

    def set_data_provider(self, provider):
        self.data_provider = provider
