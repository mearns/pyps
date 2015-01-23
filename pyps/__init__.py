#! /usr/bin/env python
# vim: set fileencoding=utf-8: 

"""
The toplevel module for the pyps package.
"""

import abc

from docit import *

class Point(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def coords(self):
        """
        Returns a two-tuple of floats, giving the X and Y coordinates of the
        point, respectively.
        """
        raise NotImplementedError()

    def __len__(self):
        return 2;

    def __getitem__(self, idx):
        try:
            return self.coords()[idx]
        except IndexError, e:
            if idx >= 2:
                raise IndexError("Points have exactly two elements.")
            raise

    @property
    def x(self):
        return self.coords()[0]

    @property
    def y(self):
        return self.coords()[1]

    def __str__(self):
        coords = self.coords()
        return "(%s,%s)" % (coords[0], coords[1])

    def __repr__(self):
        return "%s%s" % (type(self).__name__, self.__str__())



class Pt(Point):
    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        self.__coords = (x, y)

    def coords(self):
        return self.__coords

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y





