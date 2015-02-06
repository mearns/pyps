#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps import geom
import abc

class Transform(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def to_local(self, pt):
        """
        Returns a new `~pyps.geom.Point` object dynamically linked to the given ``pt``
        which maps the given point from the parent into the local coordinate system.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def to_global(self, pt):
        """
        Returns a new `~pyps.geom.Point` object dynamically linked to the given ``pt``
        which maps the given point from the local into the parent coordinate system.
        """
        raise NotImplementedError()
        

class Translation(Transform):
    def __init__(self, dx=0, dy=0):
        self._dx = geom.Float.cast(dx)
        self._dy = geom.Float.cast(dy)
        self._mdx = geom.Negative(self._dx)
        self._mdy = geom.Negative(self._dy)

    def to_global(self, pt):
        return geom.Point.cast(pt).translate(self._dx, self._dy)

    def to_local(self, pt):
        return geom.Point.cast(pt).translate(self._mdx, self._mdy)
    
