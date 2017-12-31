#!/bin/env python
# coding: utf8

import os
import shutil
from tempfile import mkdtemp

from comparer import Compare
from compiler import Compiler, CompileException
from datautils import get_out_data, get_data_path
from db import get_job, Solutions
from executor import Executor, ExecuteException
from models import Problems
from utils import logger, cfg, is_debug


class WorkerIsBusy(Exception):
    pass


class LanguageConf(object):
    lang_mapping = {
        1: {
            'ext': 'c',
            'args': ['gcc', "Main.c", "-o", "Main", "-fno-asm", "-O2", "-Wall", "-lm", "--static"]
        },
        2: {
            'ext': 'cpp',
            'args': ['g++', "Main.cpp", "-o", "Main", "-fno-asm", "-O2", "-Wall", "-lm", "--static"]
        }
    }

    def get_config(self, language):
        if language in self.lang_mapping:
            return self.lang_mapping[language]
        raise Exception('language not found')


class Worker(object):
    path = None
    solution = None
    problem = None
    busy = False

    def __init__(self, worker_id):
        super(Worker, self).__init__()
        self.busy = False
        self.worker_id = worker_id
        self.change_working_dir()
        self.lang_conf = LanguageConf()

    def is_busy(self):
        return self.busy

    def update_solution(self, result, info=None):
        self.solution.result = result
        if info:
            # reset info
            self.solution.compile_info = ''
            self.solution.runtime_info = ''
            # remember result
            self.solution.time_cost = info.time_cost
            self.solution.memory_cost = info.memory_cost
        self.solution.save()

    def process(self, solution: Solutions):
        logger.info('process job, %s', solution)
        self.busy = True
        self.solution = solution
        self.problem = Problems.get(Problems.id == self.solution.origin_problem)
        try:
            self.compile()
            self.execute()
        except CompileException as e:
            logger.error('Compile Error: ' + e.args[0])
            self.solution.result = self.solution.COMPILE_ERROR
            self.solution.compile_info = e.args[0]
            self.solution.save()
        except ExecuteException as e:
            self.update_solution(Solutions.TIME_LIMIT)
            logger.error('Execute failed', e.args, self.solution)
        finally:
            self.clean()

    def compile(self):
        logger.info('Compiling {id}'.format(id=self.solution.id))
        self.update_solution(Solutions.COMPILING)
        compiler = Compiler()
        ret = compiler.compile(self.solution.code, self.lang_conf.get_config(self.solution.language))
        if ret is not None:
            raise CompileException(ret)

    def execute(self):
        logger.info('Executing {id}'.format(id=self.solution.id))
        self.prepare_environment()
        executor = Executor(self.problem.time_limit)
        result = executor.execute()
        logger.info('Execute result: %s', result)
        if int(result.result) == Solutions.ACCEPTED:
            self.judge(result)
        else:
            self.solution.result = result.result
            if result.error:
                self.solution.runtime_info = result.error
            else:
                self.solution.runtime_info = ""
            self.solution.save()

    def judge(self, result):
        logger.info('Judging {id}'.format(id=self.solution.id))

        comparer = Compare()
        compare_result = comparer.compare(result.user_out, get_out_data(self.solution.origin_problem))
        logger.info('Judged {id}: result = {ret}'.format(id=self.solution.id, ret=compare_result))

        if compare_result == 'pe':
            self.update_solution(Solutions.PRESENTATION_ERROR, result)
        elif compare_result:
            self.update_solution(Solutions.ACCEPTED, result)
        else:
            self.update_solution(Solutions.WRONG_ANSWER, result)

    def __del__(self):
        self.clean()

    def clean(self):
        self.busy = False
        if self.path and not is_debug():
            logger.info("Clean working dir {path}".format(path=self.path))
            os.chdir(self.path)
            os.system('rm -rf *')
            os.rmdir(self.path)

    def change_working_dir(self):
        self.path = mkdtemp(prefix='judge_')

        logger.info('worker #{id} dir is {path}'.format(id=self.worker_id, path=self.path))

        shutil.chown(self.path, cfg.client.user, cfg.client.group)
        os.chdir(self.path)

    def prepare_environment(self):
        self.place_user_input()
        self.write_case_config()

    def place_user_input(self):
        origin_path = get_data_path(self.solution.origin_problem, 'in')
        shutil.copyfile(origin_path, "data.in")

    def write_case_config(self):
        file = open("case.conf", "w")
        file.write("{0}\n".format(self.problem.time_limit))
        file.write("{0}\n".format(self.problem.memory_limit))


class WorkerPool(object):
    pool = []

    def __init__(self, num):
        self.limit = num + 1
        for i in range(1, self.limit):
            self.pool[i] = None

    def get_worker(self) -> Worker:
        """
        :return: Worker
        """
        for i in range(1, self.limit):
            if isinstance(self.pool[i], Worker):
                if self.pool[i].is_busy():
                    continue
                return self.pool[i]
            # new worker
            self.pool[i] = Worker(i)
            return self.pool[i]
        # no worker available
        raise WorkerIsBusy


if __name__ == '__main__':
    worker = Worker(1)
    job = get_job()
    worker.process(job)
