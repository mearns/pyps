#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from docit import *

import abc
import collections
import math

RADS_PER_DEG = math.pi / 180.0


class Float(object):
    """
    Dynamic encapsulation of a floating point value.

    Concrete subclasses must implement the `get_float` method to resolve
    the value.
    """

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def cast(other, error_message=None):
        if isinstance(other, Float):
            return other
        elif isinstance(other, (float, int, long)):
            return FixedFloat(float(other))
        raise TypeError(error_message or ('Could not cast to a Float: %r' % (other,)))


    @abc.abstractmethod
    def get_float(self):
        """
        Resolves the value, returning a ``float`` value.

        Concrete base classes must implement this method.

        .. seealso:: `__float__`
        """
        return float(self)

    @docit
    def __float__(self):
        """
        Implements casting this value to a ``float`` with the built in
        `~python.float` function. This resolves the object by returning the current
        value.

        This simply delegates to `get_float`.
        """
        return self.get_float()

    def __str__(self):
        """
        The default string representation of this value is simply the resolved value.
        """
        return "%s" % (float(self),)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, float(self))


class FixedFloat(Float):
    """
    A `Float` object with a static value.
    """
    def __init__(self, value):
        """
        :param value:   Anything castable to with `~python.float` giving the
            fixed value of this object.
        """
        self.set(value)

    def get_float(self):
        return self._float_value

    def set(self, val):
        """
        Sets the value of the float, casting the given ``val`` to a `~python.float`.
        """
        self._float_value = float(val)

    @docit
    def __cmp__(self, other):
        """
        `FixedFloat` objects can be compared to numerical value on the basis of
        their numerical value.
        """
        if isinstance(other, (int, long, float)):
            return cmp(self._float_value, other)
        return NotImplemented

    @docit
    def __rcmp__(self, other):
        """
        `FixedFloat` objects can be compared to numerical value on the basis of
        their numerical value.
        """
        if isinstance(other, (int, long, float)):
            return cmp(other, self._float_value)
        return NotImplemented


class Length(Float):
    """
    Represents a length. This is a `Float` with the added requirement that is cannot be negative.
    """
    @staticmethod
    def cast(other, error_message=None):
        """
        An object that is alreayd a `Length` is simply returned.

        A non-negative ``float``, ``int``, or ``long`` value is returned as a `FixedLength`
        object.
        """
        if isinstance(other, Length):
            return other
        elif isinstance(other, (float, int, long)):
            if other < 0:
                raise ValueError(error_message or ('Length must be non-negative: %r' % (other,)))
            return FixedLength(float(other))
        raise TypeError(error_message or ('Could not cast to a Length: %r' % (other,)))


class FixedLength(FixedFloat, Length):
    """
    A `Length` object with a fixed value.
    """
    pass

class Abs(Length):
    def __init__(self, other):
        self.__other = Float.cast(other)

    def get_float(self):
        return abs(float(self.__other))

class Negative(Float):
    """
    A dynamic `Float` which is always the negative of another `Float`.
    """
    def __init__(self, other):
        self.__other = Float.cast(other)

    def get_float(self):
        return -(self.__other.get_float())

    def __str__(self):
        return '-%s' % self.__other


class Angle(Float):
    """
    Represents an angle in degrees. This is a `Float` with a specific interpretation
    and additional helpful APIs.
    """
    @staticmethod
    def cast(other, error_message=None):
        if isinstance(other, Angle):
            return other
        elif isinstance(other, (float, int, long)):
            return FixedAngle(other)
        raise TypeError(error_message or ('Could not cast to a Angle: %r' % (other,)))

    @property
    def radians(self):
        return Product(self, RADS_PER_DEG)

    def get_radians(self):
        """
        Returns a ``float`` representing the current value of the angle, in radians.
        """
        return float(self.radians)

class FixedAngle(FixedFloat, Angle):
    pass

class ReducedAngle(Angle):
    """
    Always resolves to an angle in the closed range [0, 360] degrees.
    """
    def __init__(self, other):
        self.__other = Angle.cast(other)

    def get_float(self):
        angle = float(self.__other)
        while angle < 0:
            angle += 360.0
        while angle > 360.0:
            angle -= 360.0
        return angle

class StrictAngle(ReducedAngle):
    """
    Like `ReducedAngle`, but resolves to the half-closed range [0, 360). A value
    that would resolve as 360 with `ReducedAngle` will resolve as 0 here.
    """
    def get_float(self):
        angle = super(StrictAngle, self).get_float()
        if angle == 360.0:
            return 0.0
        return angle

class SymmetricAngle(Angle):
    """
    Like `ReducedAngle`, except instead of returning a value in the closed range [0, 360],
    it alwsys resolves to a value in the closed range [-180, 180].
    """
    def __init__(self, other):
        self.__other = Angle.cast(other)

    def get_float(self):
        angle = float(self.__other)
        while angle < -180.0:
            angle += 360.0
        while angle > 180.0:
            angle -= 360.0
        return angle
    
class ComplementaryAngle(Angle):
    def __init__(self, other):
        self.__other = Angle.cast(other)

    def get_float(self):
        angle = float(self.__other)
        while angle < 0:
            angle += 360.0
        while angle > 360:
            angle -= 360
        while angle > 90:
            angle -= 90
        return 90.0 - angle

class SupplementaryAngle(Angle):
    def __init__(self, other):
        self.__other = Angle.cast(other)

    def get_float(self):
        angle = float(self.__other)
        while angle < 0:
            angle += 360.0
        while angle > 360:
            angle -= 360
        while angle > 180:
            angle -= 180
        return 180.0 - angle

class ReflexAngle(Angle):
    def __init__(self, other):
        self.__other = Angle.cast(other)

    def get_float(self):
        angle = float(self.__other)
        while angle < 0:
            angle += 360.0
        while angle > 360:
            angle -= 360
        return 360.0 - angle


class PairFloat(Float):
    """
    Abstract base class for `Float` subclasses that are based on two other `Float` objects.
    """
    def __init__(self, a, b):
        self.__a = Float.cast(a)
        self.__b = Float.cast(b)
        
    @abc.abstractmethod
    def combine(self, a, b):
        """
        Combine the two resolved values in the appropriate way.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def to_string(self, a, b):
        """
        Create a string representing the appropriate combination of the two component objects.
        """
        raise NotImplementedError()

    @docit
    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.__a, self.__b)

    def get_float(self):
        """
        Delegates to `combine`, passing the two component values, resolved.
        """
        return self.combine(float(self.__a), float(self.__b))

    @docit
    def __str__(self):
        """
        Delegates to `to_string`, passing the two component objects.
        """
        return self.to_string(self.__a, self.__b)

class PairLength(Length, PairFloat):
    def __init__(self, a, b):
        PairFloat.__init__(self, Length.cast(a), Length.cast(b))

        
class DifferenceMixin(object):
    """
    Dynamic representation of a `Float` which is the difference of two other `Float` objects.
    """
    def combine(self, a, b):
        return a-b

    def to_string(self, a, b):
        return "(%s - %s)" % (a, b)
class Difference(DifferenceMixin, PairFloat):
    pass
class DifferenceAngle(Angle, Difference):
    pass
class DifferenceLength(DifferenceMixin, PairLength):
    def combine(self, a, b):
        return abs(a - b)

class QuotientMixin(object):
    """
    Dynamic representation of a `Float` which is the quotient of two other `Float` objects.
    """
    def combine(self, a, b):
        return a / b

    def to_string(self, a, b):
        return "(%s / %s)" % (a, b)
class Quotient(QuotientMixin, PairFloat):
    pass
class QuotientAngle(Angle, Quotient):
    pass
class QuotientLength(QuotientMixin, PairLength):
    pass


class NaryFloat(Float):
    """
    Abstract base class for `Float` subclasses that are based on a single operation performed
    over an arbitrary number of other `Float` values.
    """
    def __init__(self, other, *others):
        all_others = [other]
        all_others.extend(others)

        self.__others = tuple(Float.cast(other) for other in all_others)
        
    @abc.abstractmethod
    def combine(self, other, *others):
        """
        Combine the given resolved values in the appropriate way.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def to_string(self, *all_others):
        """
        Create a string representing the appropriate combination of the two component objects.
        """
        raise NotImplementedError()

    @docit
    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, ", ".join(repr(o) for o in self.__others))

    def get_float(self):
        """
        Delegates to `combine`, passing the two component values, resolved.
        """
        return self.combine(*(float(o) for o in self.__others))

    @docit
    def __str__(self):
        """
        Delegates to `to_string`, passing the two component objects.
        """
        return self.to_string(*(self.__others))

class NaryLength(Length, NaryFloat):
    def __init__(self, other, *others):
        NaryFloat.__init__(self, Length.cast(other), *(Length.cast(o) for o in others))

class PairWiseMixin(object):
    def combine(self, other, *others):
        return reduce(self.combine_pair, others, other)

    @abc.abstractmethod
    def combine_pair(self, a, b):
        raise NotImplementedError()

class SumMixin(PairWiseMixin):
    """
    Dynamic representation of a `Float` which is the sum of other `Float` objects.
    """
    def combine_pair(self, a, b):
        return a + b

    def to_string(self, *all_others):
        return "(%s)" % " + ".join(str(o) for o in all_others)

class Sum(SumMixin, NaryFloat):
    pass
class SumAngle(Angle, Sum):
    pass
class SumLength(SumMixin, NaryLength):
    pass


class ProductMixin(PairWiseMixin):
    """
    Dynamic representation of a `Float` which is the sum of other `Float` objects.
    """
    def combine_pair(self, a, b):
        return a * b

    def to_string(self, *all_others):
        return "(%s)" % " * ".join(str(o) for o in all_others)

class Product(ProductMixin, NaryFloat):
    pass
class ProductAngle(Angle, Product):
    pass
class ProductLength(ProductMixin, NaryLength):
    pass

class MeanMixin(object):
    def combine(self, other, *others):
        return reduce(lambda a,b: a + b, others, other) / float(len(others)+1)

    def to_string(self, *all_others):
        return "mean(%s)" % ", ".join(str(o) for o in all_others)

class Mean(MeanMixin, NaryFloat):
    pass
class MeanAngle(Angle, Mean):
    pass
class MeanLength(MeanMixin, NaryLength):
    pass
        

class PointPointDistance(Length):
    """
    A dynamic `Length` representing the distance between two points.
    """
    def __init__(self, pt1, pt2=0):
        """
        :param pt1: The first point. This must be castable with `Point.cast`.
        :param pt2: Optional, the second point. This must be castable with `Point.cast`.
            The default is 0, which acts as the origin (0,0).
        """
        self._pt1 = Point.cast(pt1)
        self._pt2 = Point.cast(pt2)

    def get_float(self):
        x1, y1 = self._pt1.get_coords()
        x2, y2 = self._pt2.get_coords()
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx*dx + dy*dy)

    def __str__(self):
        return "|%s -- %s|" % (self._pt1, self._pt2)

    def __repr__(self):
        return "%s(%r, %r)" % (type(self).__name__, self._pt1, self._pt2)


class Point(object):
    """
    Abstract class provides the interface for all points.

    Concrete subclasses must implement the `x` and `y` properties.

    A `Point` acts like a two-tuple of it's coordinates as :samp:`({x}, {y})`,
    by implementing the `__len__` and `__getitem__` methods.

    Note that we don't have any built in ``__eq__`` method, because points may be
    equal at one moment, and unequal at another. You can use `is_at` to determine if
    the point currently resolves to specified coordinates.
    """

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def cast(other, error_message=None):
        """
        Create a `Point` object from the given object if possible.

        If ``other`` is already a `Point` (including an instance of any subclass of `Point`),
        then it is simply returned.

        If ``other`` is a sequence of length 2, it is assumed to hold the coordinates
        of the point as :samp:`({x}, {y})`. In this case, it will create a fixed point,
        an instance of the `FixedPoint` class.

        If ``other`` is a ``float``, ``int``, or ``long`` value equal to 0, then it represents
        the *origin*, and a fixed point positioned at `(0, 0)` is returned.

        Otherwise a |TypeError| is raised with the given ``error_message``, or a default error message
        is none is provided.
        """
        if isinstance(other, Point):
            return other
        elif isinstance(other, collections.Sequence):
            if len(other) == 2:
                return FixedPoint(*other)
        elif isinstance(other, (int, float, long)):
            if other == 0:
                return FixedPoint(0, 0)

        raise TypeError(error_message or ('Could not cast to a Point: %r' % (other,)))

    def is_at(self, x, y):
        """
        Check to see if this point currently resolves to the specified x and y
        coordinates.
        """
        return (float(x) == self.get_x()) and (float(y) == self.get_y())
            
    @abc.abstractproperty
    def x(self):
        """
        A dynamic `Float` value representing the X coordinate of the point.

        .. seealso::

            `get_x`
                To resolve this property.
        """
        raise NotImplementedError()

    @abc.abstractproperty
    def y(self):
        """
        A dynamic `Float` value representing the Y coordinate of the point.

        .. seealso::

            `get_y`
                To resolve this property.
        """
        raise NotImplementedError()

    def get_x(self):
        """
        Resolves the `x` property to return the current value of the X coordinate.

        .. seealso::
            `x`
                The corresponding dynamic property
        """
        return float(self.x)

    def get_y(self):
        """
        Resolves the `y` property to return the current value of the Y coordinate.

        .. seealso::
            `y`
                The corresponding dynamic property
        """
        return float(self.y)

    def get_coords(self):
        """
        Resolves the point by returning a two-tuple of floats, giving the current 
        X and Y coordinates of the point, respectively.

        .. seealso:: `get_x`, `get_y`
        """
        return (self.get_x(), self.get_y())

    @docit
    def __len__(self):
        """
        A `Point` acts like a two-tuple over it's X and Y coordinates, so its length
        is always 2.
        """
        return 2;

    @docit
    def __getitem__(self, idx):
        """
        A `Point` acts like a two-tuple over it's `x` and `y` properties, this method
        provides indexed-access on the object. 
        """
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        raise IndexError("Points have exactly two elements.")

    @docit
    def __str__(self):
        """
        Default string representation is the conventional X-Y pair in parenthesis, separated
        by a comma, using the resolved coordinate values.
        """
        return '(%s,%s)' % self.get_coords()

    @docit
    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.x, self.y)

    def distance(self, to=0):
        """
        Returns a dynamic `PointPointDistance` object representing the distance between
        this point and the given point, which defaults to the origin at (0,0) if not given.
        """
        return PointPointDistance(self, to)

    def fix(self):
        """
        Creates and returns an instance of `FixedPoint` at the current location of this
        point.
        """
        return FixedPoint(self.get_x(), self.get_y())

    def translate(self, dx=0, dy=0):
        """
        Returns a new Point which has a translational relationship to this point.
        """
        return Translated(self, dx, dy)

    def dilate(self, scale, origin=0):
        return Dilated(self, scale, origin)


class FixedPoint(Point):
    """
    Represents a `Point` at a fixed location.
    """

    def __init__(self, x, y):
        self.__x = FixedFloat(x)
        self.__y = FixedFloat(y)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def moveTo(self, x=None, y=None):
        """
        Changes the coordinates of this point to those given.

        Values are always resolved immediately as floats, this is not the way to create a dynamic
        point.

        :param x:   Optional, the value of the X coordinate to move to, or |None|
            to leave the X coordinate alone. Default is ``None``.
        :param y:   Optional, the value of the Y coordinate to move to, or |None|
            to leave the Y coordinate alone. Default is ``None``.
        """
        if x is not None:
            self.__x.set(x)
        if y is not None:
            self.__y.set(y)

    def move(self, dx=None, dy=None):
        """
        Like `moveTo`, except the move is relative to the current location.
        """
        if dx is not None:
            self.__x.set(float(dx) + float(self.__x))
        if dy is not None:
            self.__y.set(float(dy) + float(self.__y))


class Translated(Point):
    """
    A derived point which is a specified rectangular translation from another Point.
    """
    def __init__(self, pt, dx=0, dy=0):
        """
        :param Point pt:    The `Point` from which this point is translated.
        :param Float dx:    Optional, the translation of this point from the given ``pt``,
            in the horizontal (X) direction. This is anything that can be passed to
            a `Sum` (meaning anything that can be cast to a `Float`). The default is 0.

        :param Float dy:    Optional, like ``dx``, but for the vertical translation.
            Default is 0.
        """
        self._pt = Point.cast(pt)
        self._dx = Float.cast(dx)
        self._dy = Float.cast(dy)
        self._x = Sum(self._pt.x, self._dx)
        self._y = Sum(self._pt.y, self._dy)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @docit
    def __str__(self):
        return '(%s + (%s,%s))' % (self._pt, self._dx, self._dy)

    @docit
    def __repr__(self):
        return '%s(%r, %r, %r)' % (type(self).__name__, self._pt, self._dx, self._dy)

class Dilated(Point):
    def __init__(self, pt, scale, origin=0):
        origin = Point.cast(origin)
        scale = Float.cast(scale)
        u_x = Difference(pt.x, origin.x)
        u_y = Difference(pt.y, origin.y)
        vx = Product(u_x, scale)
        vy = Product(u_y, scale)
        self._x = Sum(origin.x, vx)
        self._y = Sum(origin.y, vy)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y


        

