import json

from judge.constant import Status
from judge.log import get_logger

MAX_USER_OUT = 65536


class Result(object):
    solution_id = ...
    result = Status.ACCEPTED
    time_cost = 0
    memory_cost = 0
    error = ''
    user_out = ''

    @staticmethod
    def make(result, task_id):
        instance = Result()
        instance.solution_id = task_id
        instance.result = result

        return instance

    def parse_executor_output(self, content):
        try:
            ret = json.loads(content)
            self.result = ret['status']
            self.time_cost = ret['time']
            self.memory_cost = ret['memory']
            self.error = open("user.err").read(MAX_USER_OUT)
        except FileNotFoundError as e:
            get_logger().error('user.err not found')
            self.result = Status.RUNTIME_ERROR
            self.time_cost = 0
            self.memory_cost = 0

    def is_accept(self):
        return Status.is_accept(self.result)

    def as_dict(self):
        return {
            'solution_id': self.solution_id,
            'result': self.result,
            'error': self.error,
            'time_cost': self.time_cost,
            'memory_cost': self.memory_cost
        }

    def __str__(self):
        return "solution_id: {id},result:{result}," \
               "time_cost:{time_cost},memory_cost:{memory_cost}," \
               "error:{error}" \
            .format(id=self.solution_id, result=self.result, time_cost=self.time_cost,
                    memory_cost=self.memory_cost, error=self.error)

    def __repr__(self):
        return self.__str__()
