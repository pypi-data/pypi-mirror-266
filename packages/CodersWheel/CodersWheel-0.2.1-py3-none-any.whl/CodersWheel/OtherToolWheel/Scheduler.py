# -*- coding: utf-8 -*-
import apscheduler


def Task():
    import time
    print(id)
    print(time.time())


def SleepScheduler(task, sleeptime=10):
    import time
    # Do task
    while 1:
        task()
        time.sleep(sleeptime)


def ThreadingScheduler(task, parameter=(), sleeptime=10):
    """
    First argument is to make sure the delay for execute the task.
    Second argument is to execute the task.
    Third argument is to the parameter for executing the task
    # TODO:  test
    """
    from threading import Timer
    Timer(sleeptime, task, parameter).start()


class SchedScheduler(object):
    def __init__(self):
        import sched, time
        # initial the class of scheduler in the sched  moudle
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def createjobs_delayrelated(self, task, delay=10, priority=1):
        # Add job
        self.scheduler.enter(delay, priority, task)

    def createjobs_delayabs(self, task, time=10, priority=1):
        # Add job
        self.scheduler.enterabs(time, priority, task)

    def Run(self):
        # run jobs
        self.scheduler.run()


class ScheduleSchedulerBase(object):
    def __init__(self, task):
        import schedule
        self.schedule = schedule
        self.task = task
        pass

    def job(self):
        import threading
        threading.Thread(target=self.task).start()

    def SetDown(self):
        self.schedule.every(10).seconds.do(self.job)
        return self

    def run(self):
        import time
        while True:
            self.schedule.run_pending()
            time.sleep(1)


class ScheduleScheduler(ScheduleSchedulerBase):
    def __init__(self, task):
        super(ScheduleScheduler, self).__init__(task)

    def SetDown(self):
        self.schedule.every().day.at("9:00").do(self.job)
        return self

if __name__ == '__main__':
    Timer = ScheduleSchedulerBase(Task)
    Timer.SetDown().run()
    # TODO write aspschedule

    pass
