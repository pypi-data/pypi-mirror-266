# -*- coding:utf-8 -*-


class CoroutineWheel(object):
    def __init__(self):
        self.Coroutine = self.Coroutine_core

    def initialization(self, *args, **kwargs):
        # ---- init-----
        print('---- init-----')
        status = "init"
        return status, args, kwargs

    def Processor(self, core, *args, **kwargs):
        # -----Processor----------

        argss = None
        status = 'processed'
        return status, argss

    def StatusBar(self, status, *args, **kwargs):
        pass

    def Breaktrigger(self, situation):
        # -----Break Detector------
        return 'End'

    def Coroutine_core(self, *args, **kwargs):
        # ---- init-----
        status, args, kwargs = self.initialization(*args, **kwargs)
        # ---- init----- Done
        while 1:
            core = yield status
            # -----Break Detector------
            if self.Breaktrigger(status) == 'End':
                break
            else:
                pass
            # -----Break Detector------Done

            # -----Processor----------
            status, argss = self.Processor(core)
            # -----Processor---------- Done
            # -----StatusBar-----------
            self.StatusBar(status)
            # -----StatusBar-----------


if __name__ == '__main__':
    pass
