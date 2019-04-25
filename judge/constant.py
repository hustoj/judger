#!/bin/env python3


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
