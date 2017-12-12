#!/bin/env python3
# coding: utf8

import os

from utils import cfg


def get_in_data(sid):
    path = get_data_path(sid, 'in')
    if not os.path.exists(path):
        raise RuntimeError('output data not exist')
    f = open(path)
    return f.read()


def get_out_data(sid):
    path = get_data_path(sid, 'out')
    if not os.path.exists(path):
        raise RuntimeError('output data not exist')
    f = open(path)
    return f.read()


def get_data_path(sid, ext):
    """
    :param sid: Solutions
    :param ext: string
    :return:
    """

    return '{path}/{id}/{id}.{ext}'.format(path=cfg.data.path, id=sid, ext=ext)
