#!/bin/env python3
# coding: utf8
import pylibconfig2


def load_config(path):
    f = open(path)
    return pylibconfig2.Config(f.read())
