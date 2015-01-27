#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

import abc
import collections

class Point(object):
    """
    Abstract class provides the interface for all points.
    """

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def cast(other):
        if isinstance(other, Point):
            return other
        elif isinstance(other, collections.Sequence):
            if len(other) == 2:
                return Pt(*other)
        elif isinstance(other, (int, float, long)):
            if other == 0:
                return Pt(0, 0)

        raise TypeError('Could not cast to a Point: %r' % (other,))
            

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

    def translate(self, dx=0, dy=0):
        return Translation(self, dx, dy)

    def pin(self):
        """
        Creates and returns an instance of `Pt` at the current location of this
        point.
        """
        return Pt(*(self.coords()))


class Pt(Point):
    """
    Represents a `Point` at a fixed location.
    """

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


class Length(object):
    """
    Represents a length.
    """

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def cast(self, other):
        if isinstance(other, Length):
            return other
        elif isinstance(other, (float, int, long)):
            return FixedLength(other)
        raise TypeError('Could not cast to a Length: %r' % (other,))

    @abc.abstractmethod
    def __float__(self):
        raise NotImplementedError()

    def __str__(self):
        return "%s" % (float(self),)
        
class FixedLength(Length):
    def __init__(self, length):
        self.__length = float(length)

    def __float__(self):
        return self.__length


class Translation(Point):
    """
    A derived point which is a fixed translation from another Point.
    """
    def __init__(self, origin, dx=0, dy=0):
        self.__origin = Point.cast(origin)
        self.__dx = float(dx)
        self.__dy = float(dy)

    def coords(self):
        ox, oy = self.__origin.coords()
        return (ox + self.__dx, oy + self.__dy)



if __name__ == '__main__':
    pass


