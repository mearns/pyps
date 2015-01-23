#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

import abc

class Writer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def write(self, ostream, *shapes):
        raise NotImplementedError()

