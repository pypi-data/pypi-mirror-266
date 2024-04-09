# -*- coding: utf-8 -*-
# # Copyright by sn0wfree 2018
# ----------------------------

from CodersWheel.api import API

__Version__ = API.__Version__
__Author__ = API.__Author__
__Description__ = API.__Description__


class PersonalWheel(object):

    def __init__(self):
        self.API = API.API()


if __name__ == '__main__':
    pass
