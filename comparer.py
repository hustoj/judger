#!/bin/env python3
# coding: utf8

from utils import is_debug


def strip_line(string):
    return string.replace(' ', '').replace('\t', '').replace("\n", '')


class Compare(object):
    def compare(self, standard, user):
        """
            :type standard str
            :type user str
        """
        if is_debug():
            print("compare:\n--\n{standard}\n--\n{user}--".format(standard=standard, user=user))
        if standard.rstrip() == user.rstrip():
            return True
        if self.compare_without_blank(standard, user):
            return 'pe'
        return False

    def compare_without_blank(self, standard, user):
        return strip_line(standard) == strip_line(user)


if __name__ == '__main__':
    compare = Compare()
    print(compare.compare('aaaa', 'bbb'))
    print(compare.compare('aaaa', 'aaa'))
    print(compare.compare('aaaa', 'aaaa'))
    print(compare.compare('aaaa', ' aaaa  '))
    print(compare.compare('aaaa', 'aa aa  '))
    print(compare.compare("aa\nbb", "aa\n\nbb"))
