#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

"""
The `shapes` module defines the various built in shape objects.
"""

from docit import *
import math
import abc

from pyps import geom


TAU = 2.0 * math.pi


class Paintable(object):
    def __init__(self, stroke=None, fill=None, stroke_width=1.0):
        self._stroke = stroke
        self._fill = fill
        self._stroke_width = geom.Length.cast(stroke_width, 'Stroke-width must be a length: %r' % (stroke_width,))

    @property
    def fill(self):
        return self._fill

    @property
    def stroke(self):
        return self._stroke

    @property
    def stroke_width(self):
        return self._stroke_width

    def has_fill(self):
        return self._fill is not None

    def has_stroke(self):
        return self._stroke is not None


class Path(Paintable):

    def __init__(self, paint=None, **kwargs):
        self._components = []
        if paint is not None:
            kwargs.setdefault('stroke', paint.stroke)
            kwargs.setdefault('stroke_width', paint.stroke_width)
            kwargs.setdefault('fill', paint.fill)
        super(Path, self).__init__(**kwargs)

    def __str__(self):
        return '\n    '.join(' '.join(str(x) for x in comp) for comp in self._components)

    def __iter__(self):
        return iter(self._components)

    def __len__(self):
        return len(self._components)

    def __getitem__(self, idx):
        return self._components[idx]

    def _add(self, command, *args):
        self._components.append(tuple([command] + list(args)))
        return self

    def moveTo(self, pt):
        #moveto
        pt = geom.Point.cast(pt, 'Move-to argument must be a point: %r' % (pt,))
        return self._add('M', pt.x, pt.y)
        
    def lineTo(self, pt):
        #lineto
        pt = geom.Point.cast(pt, 'Line-to argument must be a point: %r' % (pt,))
        return self._add('L', pt.x, pt.y)

    def move(self, dx, dy):
        #rmoveto
        dx = geom.Length.cast(dx, 'Move dx argument must be a length: %r' % (dx,))
        dy = geom.Length.cast(dy, 'Move dy argument must be a length: %r' % (dy,))
        return self._add('m', float(dx), float(dy))

    def line(self, dx, dy):
        #rlineto
        #rmoveto
        dx = geom.Length.cast(dx, 'Line dx argument must be a length: %r' % (dx,))
        dy = geom.Length.cast(dy, 'Line dy argument must be a length: %r' % (dy,))
        return self._add('l', float(dx), float(dy))

    def arc(self, center, radius, start_deg=0, stop_deg=360, ccw=True):
        #arc
        center = geom.Point.cast(center, 'Center of arc must be a point: %r' % (center,))
        radius = geom.Length.cast(radius, 'Radius of arc must be a length: %r' % (radius,))
        start_deg = geom.Angle.cast(start_deg, 'Start-deg of arc must be an angle: %r' % (start_deg,))
        stop_deg = geom.Angle.cast(stop_deg, 'Stop-deg of arc must be an angle: %r' % (stop_deg,))
        return self._add('a', center.x, center.y, float(radius), float(start_deg), float(stop_deg), bool(ccw))

    #def curveTo(self, end, cp1, cp2):
    #    #curveto
    #
    #def curve(self, edx, edy, cp1dx, cp1dy, cp2dx, cp2dy):
    #    #rcurveto


class Shape(object):
    """
    This is the base class for all shapes. It defines the interface for shapes
    and provides some helper functions for those shapes.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, title=None):
        self._title = title

    def set_title(self, title):
        self._title = title

    def title(self):
        return self._title

    def __str__(self):
        if self._title:
            return self._title
        return repr(self)

    @abc.abstractmethod
    def hittest(self, x, y):
        """
        Checks to see if the given point is contained by this shape. This
        should include exactly those points that would be drawn on by this
        shape, either for outline or fill.

        :param float x: The X coordinate of the point to test.
        :param float y: The Y coordinate of the point to test.

        :returns bool:
            Return |TRUE| if and only if the point is contained by this shape,
            |FALSE| otherwise.

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def boundingbox(self):
        """
        Returns a `BoundingBox` which completely contains this shape. Ideally,
        this should be a minimum bounding box, i.e., the smallest possible
        box that contains the entire shape. But this is not strictly necessary
        if you have a hard time computing that.

        :rtype: `BoundingBox`
        """
        raise NotImplementedError()

    def boundingpoly(self, complexity=0.5):
        """
        Returns a polygon which entirely contains this shape. This is a
        generalization of the `boundingbox` method and it is acceptable to
        simply delegate to that method, as the default implementation does.

        But ideally, this will be a bounding polygon which fits more tightly
        around the actual shape, at the cost of being a more complex polygon.

        The optional ``complexity`` parameter specifies a heuristic of how
        complex the ploygon should be. This is widely open to interpretation
        but you should consider a value of ``0.0`` to be minimally complex
        (probably just delegating to `boundingbox`), and a value of ``1.0`` to
        be maximally complex, with values corresponding to an appropriate
        intermediate complexity.

        For instance, for a circle, complexity of ``0.0`` might correspond to
        just the `boundingbox`, while complexity of ``1.0`` might have a
        100-sided regular polygon which circumscribes the circle. A complexity
        of ``0.5`` would be somewhere in between, perhaps a 12-sided regular
        polygon.

        :param float complexity:    Optional parameter specifying a complexity
            heuristic for the polygon as described above. The range should be
            from ``0.0`` (minimum complexity) to ``1.0`` (maximum complexity).
            The default value is ``0.5``.

        :rtype: `Polygon`.
        """
        #FIXME XXX: BoundingBox will need to extend some kind of Polygon class.
        return self.boundingbox()

    @abc.abstractmethod
    def render(self, capabilities=[]):
        raise NotImplementedError()
        

class PaintableShape(Shape, Paintable):
    def __init__(self, title=None, **kwargs):
        Shape.__init__(self, title)
        kwargs.setdefault('stroke', (0, 0, 0))
        Paintable.__init__(self, **kwargs)


class BoundingBox(object):
    """
    A `BoundingBox` is a rectangle which is orthogonal to the X and Y axes.
    It is typically used to represent the minimum bounding box around a shape,
    and is returned by `Shape.boundingbox`.

    A `BoundingBox` instance is defined by two opposite corners of the box.
    Either pair of opposite corners, in either order, can be used. These points
    can be dynamic points; all methods of the bounding box work dynamically
    based on the current positions of the given points.
    """

    #FIXME XXX: Make this a `Shape`.

    def __init__(self, pt1, pt2):
        pt1 = geom.Point.cast(pt1)
        pt2 = geom.Point.cast(pt2)
        self._lowerleft = self._LowerLeft(pt1, pt2)
        self._lowerright = self._LowerRight(pt1, pt2)
        self._upperleft = self._UpperLeft(pt1, pt2)
        self._upperright = self._UpperRight(pt1, pt2)

    def width(self):
        """
        Returns the width of the bounding box.
        """
        return self._lowerright.x - self._lowerleft.x

    def height(self):
        """
        Returns the height of the bounding box.
        """
        return self._upperleft.y - self._lowerleft.y

    def area(self):
        return self.width()*self.height()

    @property
    def lowerleft(self):
        """
        Returns a dynamic point representing the lower left corner of the box,
        which is the point with the minimum X and minimum Y coordinates.

        :rtype: `~geom.Point`
        """
        return self._lowerleft

    @property
    def lowerright(self):
        """
        Returns a dynamic point representing the lower right corner of the box,
        which is the point with the maximum X and minimum Y coordinates.

        :rtype: `~geom.Point`
        """
        return self._lowerright

    @property
    def upperleft(self):
        """
        Returns a dynamic point representing the upper left corner of the box,
        which is the point with the minimum X and maximum Y coordinates.

        :rtype: `~geom.Point`
        """
        return self._upperleft

    @property
    def upperright(self):
        """
        Returns a dynamic point representing the upper right corner of the box,
        which is the point with the maximum X and maximum Y coordinates.

        :rtype: `~geom.Point`
        """
        return self._upperright

    ### We could easily have done a common base class for all of these, and made
    # each specific implementation very small and simple, but they are already
    # such trivial implementations that the only reason to do that would be to
    # save key strokes. So why not put in the effort once at coding time and
    # improve performance a bit.

    class _LowerLeft(geom.Point):
        """
        Simple dynamic point that represents the lower left point of the box
        defined by two opposite points, ``pt1`` and ``pt2``.

        The lower left has minimum X coordinate and minimum Y coordinate of
        the given points.
        """
        def __init__(self, pt1, pt2):
            """
            :param pt1: One of two opposite points that define the box.
            :type pt1: Anything castable by `~geom.Point`.

            :param pt2: The other of the two opposite points that define the box.
            :type pt2: Anything castable by `~geom.Point`.

            """
            self._pt1 = pt1
            self._pt2 = pt2

        def coords(self):
            """
            Implements `geom.Point.coords <geom.Point.coords>` by dynamically choosing
            the correct limiting coordinates of the box.
            """
            c1 = self._pt1.coords()
            c2 = self._pt2.coords()
            return min(c1[0], c2[0]), min(c1[1], c2[1])

    class _UpperLeft(geom.Point):
        """
        Like `_LowerLeft`, but representing the *upper* left point of the box.

        The upper left has minimum X coordinate and maximum Y coordinate of
        the given points.
        """
        def __init__(self, pt1, pt2):
            self._pt1 = pt1
            self._pt2 = pt2

        def coords(self):
            c1 = self._pt1.coords()
            c2 = self._pt2.coords()
            return min(c1[0], c2[0]), max(c1[1], c2[1])

    class _LowerRight(geom.Point):
        """
        Like `_LowerLeft`, but representing the lower *right* point of the box.

        The lower right has maximum X coordinate and minimum Y coordinate of
        the given points.
        """
        def __init__(self, pt1, pt2):
            self._pt1 = pt1
            self._pt2 = pt2

        def coords(self):
            c1 = self._pt1.coords()
            c2 = self._pt2.coords()
            return max(c1[0], c2[0]), min(c1[1], c2[1])

    class _UpperRight(geom.Point):
        """
        Like `_LowerLeft`, but representing the *upper* *right* point of the box.

        The upper right has maximum X coordinate and maximum Y coordinate of
        the given points.
        """
        def __init__(self, pt1, pt2):
            self._pt1 = pt1
            self._pt2 = pt2

        def coords(self):
            c1 = self._pt1.coords()
            c2 = self._pt2.coords()
            return max(c1[0], c2[0]), max(c1[1], c2[1])


class Circle(PaintableShape):

    def __init__(self, center, radius, **kwargs):
        try:
            center = geom.Point.cast(center)
        except TypeError:
            raise TypeError('Center point must be a point: %r' % (center,))

        if not isinstance(radius, (float, int, long)):
            raise TypeError('Radius must be numeric: %r' % (radius,))
        if radius <= 0:
            raise TypeError('Radius must be greater than zero: %r' % (radius,))

        self._center = center
        self._radius = float(radius)

        super(Circle, self).__init__(**kwargs)

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

    def hittest(self, x, y):
        dx = self._center.x - x
        dy = self._center.y - y
        return dx*dx + dy*dy <= self._radius * self._radius

    def boundingbox(self):
        lowerleft = self._center.translate(-(self._radius), -(self._radius))
        upperright = self._center.translate(self._radius, self._radius)
        return BoundingBox(lowerleft, upperright)

    def render(self, capabilities=[]):
        return [Path(paint=self).arc(self._center, self._radius)]

