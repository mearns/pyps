#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

"""
The `shapes` module defines the various built in shape objects.
"""

import pyps

from docit import *
import math

import abc

TAU = 2.0 * math.pi

class Shape(object):
    __metaclass__ = abc.ABCMeta


class Circle(Shape):

    def __init__(self, center, radius, **kwargs):
        super(Circle, self).__init__(**kwargs)

        if not isinstance(center, pyps.Point):
            raise TypeError('Center point must be a point: %r' % (center,))
        if not isinstance(radius, (float, int, long)):
            raise TypeError('Radius must be numeric: %r' % (radius,))
        if radius <= 0:
            raise TypeError('Radius must be greater than zero: %r' % (radius,))

        self._center = center
        self._radius = float(radius)

    @property
    def center(self):
        return self._center

    @property
    def radius(self):
        return self._radius

    @property
    def diameter(self):
        return self._radius * 2.0

    @property
    def circumference(self):
        return self._radius * TAU

    def getArea(self):
        return math.pi * (self._radius * self._radius)

