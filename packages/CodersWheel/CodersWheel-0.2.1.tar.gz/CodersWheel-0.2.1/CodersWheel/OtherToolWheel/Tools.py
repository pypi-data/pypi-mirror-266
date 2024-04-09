# -*- coding: utf-8 -*-
# # Copyright by sn0wfree 2018
# ----------------------------
import CacheFunctions
import Wrappers
import AboutDB

class Tools(object):

    def __init__(self):
        pass

    def LoadCacheFunctions(self, *args, **kwargs):

        return CacheFunctions.LastUpdatedOrderedDict

    def LoadWrappers(self):

        return Wrappers.LRUCache

    def LoadInMemoryDB(self):

        return AboutDB.inMemoryDB

    def LoadDB(self):

        return AboutDB.DBPool


if __name__ == '__main__':
    pass
