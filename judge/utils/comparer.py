#!/usr/bin/env python3
from judge.result import Status

from .utils import is_debug


def strip_line(string):
    return string.replace(' ', '') \
        .replace('\t', '') \
        .replace("\n", '')


def compare_without_blank(standard, user):
    return strip_line(standard) == strip_line(user)


class Compare:
    standard = ''
    user_out = ''

    def compare(self, standard, user):
        """
            :type standard str
            :type user str
        """
        self.standard = standard
        self.user_out = user
        if is_debug():
            self._debug_output()

        if self._is_full_match():
            return Status.ACCEPTED

        if compare_without_blank(standard, user):
            return Status.PRESENTATION_ERROR

        return Status.WRONG_ANSWER

    def _debug_output(self):
        print(f"compare:\n--\n{self.standard}\n--\n{self.user_out}--")

    def _is_full_match(self):
        return self.standard.rstrip() == self.user_out.rstrip()
