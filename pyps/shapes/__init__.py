#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

"""
The `shapes` module defines the various built in shape objects.
"""

from docit import *
import math
import abc

from pyps import geom
from pyps.art.color import Color


TAU = 2.0 * math.pi


class Paintable(object):
    """
    Simple base / mixin class for anything that has a configurable fill and stroke.
    """
    def __init__(self, paint=None, stroke=None, fill=None, stroke_width=None):
        stroke = stroke or paint.get_stroke() 
        fill = fill or paint.get_fill()
        stroke_width = stroke_width if stroke_width is not None else paint.get_stroke_width()

        self._stroke = Color.cast_or_none(stroke, 'Paintable stroke must be a color or None: %r' % (stroke,))
        self._fill = Color.cast_or_none(fill, 'Paintable fill must be a color or None: %r' % (fill,))
        self._stroke_width = geom.Length.cast(stroke_width, 'Stroke-width must be a length: %r' % (stroke_width,))

    def get_fill(self):
        return self._fill

    def get_stroke(self):
        return self._stroke

    def get_stroke_width(self):
        return self._stroke_width

    def has_fill(self):
        return self._fill is not None

    def has_stroke(self):
        return self._stroke is not None


class Path(Paintable):

    def __init__(self, paint=None, stroke=None, fill=None, stroke_width=None):
        self._components = []
        super(Path, self).__init__(paint, stroke, fill, stroke_width)

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
        return self._add('M', pt.get_x(), pt.get_y())

    def close(self):
        return self._add('X')
        
    def lineTo(self, pt):
        #lineto
        pt = geom.Point.cast(pt, 'Line-to argument must be a point: %r' % (pt,))
        return self._add('L', pt.get_x(), pt.get_y())

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
        return self._add('A', center.get_x(), center.get_y(), float(radius), float(start_deg), float(stop_deg), bool(ccw))

    def circle(self, center, radius):
        return self._add('C', center.get_x(), center.get_y(), float(radius))

    #def curveTo(self, end, cp1, cp2):
    #    #curveto
    #
    #def curve(self, edx, edy, cp1dx, cp1dy, cp2dx, cp2dy):
    #    #rcurveto



class Shape(object):
    """
    This is the base class for all shapes. It defines the interface for shapes
    and provides some helper functions for those shapes.

    The key abstract interface is:
    * <hittest>
    * <boundingbox>
    * <render>

    It is also a good idea to implement <boundingpoly>
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, title=None):
        self._title = title
        self._transforms = []

    def set_title(self, title):
        self._title = title

    def title(self):
        """
        A simple string that can be used as a title for the object. Depending on the writer,
        this may end getting included when the shape is rendered, but it will *not* be
        visible in the drawing.
        """
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

    @abc.abstractproperty
    def boundingbox(self):
        """
        Returns a `Box` which completely contains this shape. Ideally,
        this should be a minimum bounding box, i.e., the smallest possible
        box that contains the entire shape. But this is not strictly necessary
        if you have a hard time computing that.

        :rtype: `Box`
        """
        raise NotImplementedError()

    def get_boundingpoly(self, complexity=0.5):
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
        #FIXME XXX: Box will need to extend some kind of Polygon class.
        return self.boundingbox()

    @abc.abstractmethod
    def render(self, capabilities=[]):
        raise NotImplementedError()
        


class PaintableShape(Shape, Paintable):
    def __init__(self, title=None, stroke=None, fill=None, stroke_width=None):
        Shape.__init__(self, title)
        stroke = stroke or (0,0,0)
        Paintable.__init__(self, stroke=stroke, fill=fill, stroke_width=stroke_width)


class Box(Shape):
    """
    A `Box` is a rectangular `Shape` which is orthogonal to the X and Y axes.
    This is an abstract interface class, subclasses should implement
    the <get_bounds> function.
    """

    def __init__(self):
        self._lowerleft = self._LowerLeftCorner(self)
        self._lowerright = self._LowerRightCorner(self)
        self._upperleft = self._UpperLeftCorner(self)
        self._upperright = self._UpperRightCorner(self)
        super(Box, self).__init__()

    def render(self, capabilities=[]):
        return [
            Path.moveTo(self.lowerleft),
            Path.lineTo(self.upperleft),
            Path.lineTo(self.upperright),
            Path.lineTo(self.lowerright),
            Path.close(),
        ]

    @property
    def lowerleft(self):
        """
        Returns a dynamic point which represents the lower left corner of the box
        (minimum X and minimum Y).
        """
        return self._lowerleft

    @property
    def lowerright(self):
        """
        Returns a dynamic point which represents the lower right corner of the box
        (maximum X and minimum Y).
        """
        return self._lowerright

    @property
    def upperleft(self):
        """
        Returns a dynamic point which represents the upper left corner of the box
        (minimum X and maximum Y).
        """
        return self._upperleft

    @property
    def upperright(self):
        """
        Returns a dynamic point which represents the upper right corner of the box
        (maximum X and maximum Y).
        """
        return self._upperright

    @abc.abstractmethod
    def get_bounds(self):
        """
        Return a four tuple of numbers representing the limiting coordinate values
        of the box, as :samp:`({north}, {east}, {south}, {west})`, where
        :samp:`{north}` is the upper (maximum) Y coordinate, 
        :samp:`{east}` is the right-most (maximum) X coordinate, 
        :samp:`{south}` is the lower (maximum) Y coordinate, and
        :samp:`{west}` is the left-most (minimum) X coordinate, 
        """
        raise NotImplementedError()

    def get_north(self):
        return self.get_bound()[0]

    def get_south(self):
        return self.get_bound()[2]

    def get_east(self):
        return self.get_bound()[1]

    def get_west(self):
        return self.get_bound()[3]

    def get_width(self):
        """
        Returns the width of the box, the extent of the X coordinates.
        This delegates to `get_bounds`.
        """
        n, e, s, w = self.get_bounds()
        return e - w

    def get_height(self):
        """
        Returns the height of the box, the extent of the Y coordinates.
        This delegates to `get_bounds`.
        """
        n, e, s, w = self.get_bounds()
        return n - s

    def get_area(self):
        """
        Returns the current area of the box, the product of the `width <get_width>`
        and the `height <get_height>`.
        """
        return self.get_width() * self.get_height()

    def hittest(self, x, y):
        n, e, s, w = self.get_bounds()
        return (w <= x <= e) and (s <= y <= n)

    @property
    def boundingbox(self):
        return self

    def get_boundingpoly(self, quality=0.5):
        return self

    class _Corner(geom.Point):
        def __init__(self, box):
            self._box = box

        def get_coords(self):
            return (self.get_x(), self.get_y())

        @abc.abstractmethod
        def get_x(self):
            raise NotImplementedError()

        @abc.abstractmethod
        def get_y(self):
            raise NotImplementedError()

    class _LeftCorner(object):
        def get_x(self):
            return self._box.get_bounds()[3]

    class _RightCorner(object):
        def get_x(self):
            return self._box.get_bounds()[1]

    class _UpperCorner(object):
        def get_y(self):
            return self._box.get_bounds()[0]

    class _LowerCorner(object):
        def get_y(self):
            return self._box.get_bounds()[2]

    class _LowerLeftCorner(_Corner, _LeftCorner, _LowerCorner): pass
    class _LowerRightCorner(_Corner, _RightCorner, _LowerCorner): pass
    class _UpperLeftCorner(_Corner, _LeftCorner, _UpperCorner): pass
    class _UpperRightCorner(_Corner, _RightCorner, _UpperCorner): pass


class UnionBox(Box):
    """
    An abstract base class that represents the union of other `Box` objects.

    You have to subclass and implement the `iterboxes` method to iterate over the
    actual component boxes.
    """

    @abc.abstractmethod
    def iterboxes(self):
        """
        Return an interator over the component boxes.
        """
        raise NotImplementedError()

    def get_bounds(self):
        bounds = [o.get_bounds() for o in self._others]
        if not bounds:
            raise ValueError('Cannot have a union of no boxes.')
        ns = [b[0] for b in bounds]
        es = [b[1] for b in bounds]
        ss = [b[2] for b in bounds]
        ws = [b[3] for b in bounds]
        return (max(ns), max(es), min(ss), min(ws))

    def get_north(self):
        bounds = [o.get_bounds() for o in self._others]
        if not bounds:
            raise ValueError('Cannot have a union of no boxes.')
        vals = [b[0] for b in bounds]
        return max(vals)

    def get_south(self):
        bounds = [o.get_bounds() for o in self._others]
        if not bounds:
            raise ValueError('Cannot have a union of no boxes.')
        vals = [b[2] for b in bounds]
        return min(vals)
        
    def get_east(self):
        bounds = [o.get_bounds() for o in self._others]
        if not bounds:
            raise ValueError('Cannot have a union of no boxes.')
        vals = [b[1] for b in bounds]
        return max(vals)
        
    def get_west(self):
        bounds = [o.get_bounds() for o in self._others]
        if not bounds:
            raise ValueError('Cannot have a union of no boxes.')
        vals = [b[3] for b in bounds]
        return min(vals)

    def get_width(self):
        bounds = [o.get_bounds() for o in self._others]
        if not bounds:
            raise ValueError('Cannot have a union of no boxes.')
        east = max([b[1] for b in bounds])
        west = min([b[3] for b in bounds])
        return east - west

    def get_height(self):
        bounds = [o.get_bounds() for o in self._others]
        if not bounds:
            raise ValueError('Cannot have a union of no boxes.')
        north = max([b[0] for b in bounds])
        south = min([b[2] for b in bounds])
        return north - south



class Circle(PaintableShape):

    def __init__(self, center, radius, **kwargs):
        self._center = geom.Point.cast(center, "Center must be a point: %r" % (center,))
        self._radius = geom.Length.cast(radius, "Radius must be a length: %r" % (radius,))
        self._bbox = self.BBox(self)

        super(Circle, self).__init__(**kwargs)

    @property
    def center(self):
        """
        The Point representing the center of the circle.
        """
        return self._center

    @property
    def radius(self):
        """
        A `~pyps.geom.Length` representing the radius of the circle.
        """
        return self._radius

    def get_radius(self):
        """
        Returns the current radius of the circle, as a float.
        """
        return float(self._radius)

    def get_diameter(self):
        return self.get_radius() * 2.0

    def get_circumference(self):
        return self.get_radius() * TAU

    def get_area(self):
        r = self.get_radius()
        return math.pi * r * r

    def hittest(self, x, y):
        cx, cy = self.center.get_coords()
        r = self.get_radius()
        dx = cx - x
        dy = cy - y
        return (dx*dx + dy*dy) <= (r * r)

    def boundingbox(self):
        return self._bbox

    #TODO: get_boundingpoly.

    def render(self, capabilities=[]):
        return [Path(paint=self).circle(self._center, self._radius)]

    class BBox(Box):
        def __init__(self, circle):
            self._circle = circle

        def get_bounds(self):
            r = self._circle.get_radius()
            x, y = self._circle.center.get_coords()
            return (y+r, x+r, y-r, x-r)

