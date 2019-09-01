import json
import logging

LOGGER = logging.getLogger(__name__)

MAX_USER_OUT = 65536


class Status(object):
    PENDING = 0
    PENDING_REJUDGE = 1
    COMPILING = 2
    REJUDGING = 3
    ACCEPTED = 4
    PRESENTATION_ERROR = 5
    WRONG_ANSWER = 6
    TIME_LIMIT = 7
    MEMORY_LIMIT = 8
    OUTPUT_LIMIT = 9
    RUNTIME_ERROR = 10
    COMPILE_ERROR = 11

    @staticmethod
    def is_accept(result):
        return Status.ACCEPTED == int(result)


class CaseResult(object):
    solution_id = ...
    result = Status.ACCEPTED
    time_cost = 0
    peak_memory = 0
    rusage_memory = 0
    error = ''
    user_out = ''

    @staticmethod
    def make(result, task_id):
        instance = CaseResult()
        instance.solution_id = task_id
        instance.result = result

        return instance

    @classmethod
    def parse_runner(cls, content):
        LOGGER.debug("running content is [{content}]".format(content=content))
        ret = json.loads(content)
        self = cls()
        self.result = ret['status']
        self.time_cost = ret['time']
        self.peak_memory = ret['peak_memory']
        self.rusage_memory = ret['rusage_memory']

        return self

    @property
    def memory(self):
        if self.peak_memory > self.rusage_memory:
            return self.peak_memory
        return self.rusage_memory

    def update_by_case(self, case):
        """
        :param CaseResult case:
        :return: None
        """
        if not case.is_ok():
            # if failed then replace by current
            self.result = case.result
        else:
            # update cost
            self.update_cost(case)

    def update_cost(self, case):
        """
        :param CaseResult case:
        :return: None
        """
        if case.memory > self.memory:
            self.peak_memory = case.memory
        self.time_cost += case.time_cost

    def get_error(self):
        try:
            return open("user.err").read(MAX_USER_OUT)
        except FileNotFoundError as e:
            LOGGER.error('user.err not found')
            self.result = Status.RUNTIME_ERROR
            self.time_cost = 0
            self.peak_memory = 0
            self.rusage_memory = 0

    def is_ok(self):
        return Status.is_accept(self.result)

    def as_dict(self):
        return {
            'solution_id': self.solution_id,
            'result': self.result,
            'error': self.error,
            'time_cost': self.time_cost,
            'memory_cost': self.memory
        }

    def __str__(self):
        return "solution_id: {id},result:{result}," \
               "time_cost:{time_cost},memory_cost:{memory_cost}," \
               "error:{error}" \
            .format(id=self.solution_id, result=self.result, time_cost=self.time_cost,
                    memory_cost=self.memory, error=self.error)

    def __repr__(self):
        return self.__str__()
