# -*- coding: utf-8 -*-
# Copyright by sn0wfree 2018
# ----------------------------

import inspect


def get_current_function_name():
    return inspect.stack()[1][3]


class MyClass(object):

    def function_one(self):
        print("%s.%s invoked" % (
            self.__class__.__name__, self.get_current_function_name()))

    def get_current_function_name(self):

        return inspect.stack()[1][3]

    def returninspect(self):
        return inspect.stack(), len(inspect.stack())


class test(object):

    def __init__(self):
        pass

    def testd(self, d):
        return d

    def test2(self, d):
        return d


def itersubclasses(cls, _seen=None):
    """Generator over all subclasses of a given class in depth first order."""
    if not isinstance(cls, type):
        raise TypeError(
            'itersubclasses must be called with new-style classes, not %.100r' % cls)
    _seen = _seen or set()
    try:
        subs = cls.__subclasses__()
    except TypeError:   # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


class getSubClass(object):

    def __init__(self):
        # self.all_subclasses = {}
        pass

    def getsubclasses(self, cls, all_subclasses={}):

        for subclass in cls.__subclasses__():
                # print(subclass._meta.abstract)
            if (not (subclass.__name__) in all_subclasses.keys()) and (not subclass._meta.abstract):
                print(subclass.__name__)
                all_subclasses[subclass.__name__] = subclass
            all_subclasses = self.getsubclasses(
                subclass, all_subclasses=all_subclasses)
        return all_subclasses


if __name__ == '__main__':
    print(getSubClass().getsubclasses(test))

    pass
