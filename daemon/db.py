#!/bin/env python3

from models import Solutions


def get_job():
    q = Solutions.select().where(Solutions.result == 0).order_by(Solutions.id, 'asc').limit(1).get()

    return q


def update_solution(sid, result):
    solution = Solutions.select().where(Solutions.id == sid).get()
    solution.result = result
    solution.save()


if __name__ == '__main__':
    job = get_job()
    print(job.id)
    # update_solution(166, 0)
