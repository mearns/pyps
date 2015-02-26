#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

"""
The `shapes` module defines the various built in shape objects.
"""

from docit import *
import math
import abc
import collections

from pyps import geom
from pyps.art.color import Color


TAU = 2.0 * math.pi
RAD_TWO = math.sqrt(2.0)
TWO_RAD_TWO = 2.0*RAD_TWO


class Paintable(object):
    """
    Simple base / mixin class for anything that has a configurable fill and stroke.
    """
    def __init__(self, paint=None, stroke=None, fill=None, stroke_width=None):
        stroke = stroke or None if paint is None else paint.get_stroke()
        fill = fill or None if paint is None else paint.get_fill()
        stroke_width = stroke_width if stroke_width is not None else (1.0 if paint is None else paint.get_stroke_width())

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

class CompoundIterator(collections.Iterator):
    def __init__(self, *iterables):
        self._iterators = [iter(i) for i in iterables]
        self._length = len(iterables)
        self._current = 0

    def next(self):
        while True:
            if self._current >= self._length:
                raise StopIteration()
            try:
                return self._iterators[self._current].next()
            except StopIteration:
                self._current += 1

class ShapeMeta(abc.ABCMeta):

    class _LabeledObject(object):
        def __init__(self, func, labels):
            self.func = func
            self.labels = labels

    class _LabeledPoint(_LabeledObject): pass
    class _LabeledLength(_LabeledObject): pass


    @staticmethod
    def point(*args):
        """
        A decorator for creating labeled points in a class descriptor.

        Write a method which returns a dynamic `~pyps.geom.Point` object, and
        decorate it with this, then the metaclass will automatically add it to the
        dictionary of labeled points. Note that the decorated function will also be
        removed from the class dict, so it won't exist as a function any more,
        which is appropriate because transformations cant use those, they can only
        use labeled points.

        The name of the decorated function is used as the primary label for the
        point. If you invoke without any arguments (e.g., ``@point`` or ``@point()``)
        then that is the only key it can be accessed with. Otherwise, any additional
        strings you pass in as positional arguments will be used as additional _non-canonical_
        labels for the point as well.
        """
        if len(args) == 1 and callable(args[0]):
            func = args[0]
            return ShapeMeta._LabeledPoint(func, [])
        else:
            labels = args
            def wrapper(func):
                return ShapeMeta._LabeledPoint(func, labels)
            return wrapper

    @staticmethod
    def length(*args):
        """
        Like the `point` decorator, but for creating labeled lengths instead of points.
        """
        if len(args) == 1 and callable(args[0]):
            func = args[0]
            return ShapeMeta._LabeledLength(func, [])
        else:
            labels = args
            def wrapper(func):
                return ShapeMeta._LabeledLength(func, labels)
            return wrapper

    def __new__(meta, name, bases, dct):
        
        points = {}
        _pointkeys = []
        lengths = {}
        _lengthkeys = []
        remove = set()
        for k, v in dct.iteritems():
            if isinstance(v, ShapeMeta._LabeledPoint):
                labels = [k]
                _pointkeys.append(k)
                labels.extend(v.labels)
                for label in labels:
                    if label in points:
                        raise KeyError('Duplicate labeled point: %s' % (label,))
                    points[label] = v.func
                remove.add(k)
            elif isinstance(v, ShapeMeta._LabeledLength):
                labels = [k]
                _lengthkeys.append(k)
                labels.extend(v.labels)
                for label in labels:
                    if label in lengths:
                        raise KeyError('Duplicate labeled length: %s' % (label,))
                    lengths[label] = v.func
                remove.add(k)

        #remove all the attributes we just captured as points and lengths.
        for k in remove:
            del(dct[k])

        _pointkeys = tuple(_pointkeys)
        _lengthkeys = tuple(_lengthkeys)

        def method(func):
            return dct.setdefault(func.__name__, func)

        _class = None

        #Implement the point functions for the class.
        @method
        def get_point(self, key):
            """
            """
            try:
                func = points[key]
            except KeyError:
                return super(_class, self).get_point(key)
            return func(self)

        #FIXME: This isn't working real well, but it's a start. US-SHP16 will help.
        if _pointkeys:
            get_point.__doc__ += '\n\nThis class provides the following labaled points:\n\n'
            for k in _pointkeys:
                get_point.__doc__ += '``\'%s\'``\n' % k
                func = points[k]
                get_point.__doc__ += '\n'.join('        ' + line for line in (func.__doc__.splitlines() if func.__doc__ else []) if line.strip())
                get_point.__doc__ += '\n'
        else:
            get_point.__doc__ += '\n\nThis class does not provide any labeled points.\n\n'

        @method
        def point_keys_iter(self):
            """
            Iterator over all the canonical keys that can be accepted by `get_point`.
            """
            #FIXME: If there are duplicates, this won't be right.
            return CompoundIterator(_pointkeys, super(_class, self).point_keys_iter())

        @method
        def point_count(self):
            return len(_pointkeys) + super(_class, self).point_count()

        #Implement the length functions for the class.
        @method
        def get_length(self, key):
            """
            """
            try:
                func = lengths[key]
            except KeyError:
                return super(_class, self).get_length(key)
            return func(self)

        if _lengthkeys:
            get_length.__doc__ += '\n\nThis class provides the following labaled lengths:\n\n'
            for k in _lengthkeys:
                get_length.__doc__ += '``\'%s\'``\n' % k
                func = lengths[k]
                get_length.__doc__ += '\n'.join('        ' + line for line in (func.__doc__.splitlines() if func.__doc__ else []) if line.strip())
                get_length.__doc__ += '\n'
        else:
            get_length.__doc__ += '\n\nThis class does not provide any labeled lengths.\n\n'


        @method
        def length_keys_iter(self):
            """
            Return a sequence of all the canonical keys that can be accepted by `get_length`.
            """
            #FIXME: If there are duplicates, this won't be right.
            return CompoundIterator(_lengthkeys, super(_class, self).length_keys_iter())

        _class = super(ShapeMeta, meta).__new__(meta, name, bases, dct)
        return _class
        
    

class Shape(object):
    """
    This is the base class for all shapes. It defines the interface for shapes
    and provides some helper functions for those shapes.

    The key abstract interface is:
    * `hittest`
    * `boundingbox`
    * `render`

    It is also a good idea to implement `boundingpoly`
    """

    __metaclass__ = ShapeMeta

    def __init__(self, title=None):
        self._title = title
        self.__points_view = self.PointView(self)
        self.__lengths_view = self.LengthView(self)

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
        #TODO XXX: Box will need to extend some kind of Polygon class.
        return self.boundingbox()

    @abc.abstractmethod
    def render(self, capabilities=[]):
        raise NotImplementedError()

    @property
    def points(self):
        """
        Convenience property that provides a mapping view of the labeled points in this shape,
        as accessible with `get_point`.

        Returns an instance of `PointView`.
        """
        return self.__points_view

    @property
    def lengths(self):
        """
        Convenience property that provides a mapping view of the labeled lengths in this shape,
        as accessible with `get_length`.

        Returns an instance of `LengthView`.
        """
        return self.__lengths_view

    class _MappingView(collections.Mapping):
        def __getattr__(self, name):
            try:
                return self.__getitem__(name)
            except KeyError:
                raise AttributeError('No such attribute: %s' % (name,))

    class PointView(_MappingView):
        """
        A simple utility class that provides a read-only mapping view of the labeled points of a shape,
        as with `get_point`.
        """
        def __init__(self, shape):
            self.__shape = shape

        def __len__(self):
            return self.__shape.point_count()

        def __iter__(self):
            return self.__shape.point_keys_iter()

        def __getitem__(self, key):
            return self.__shape.get_point(key)

    class LengthView(_MappingView):
        """
        A simple utility class that provides a read-only mapping view of the labeled lengths of a shape,
        as with `get_length`.
        """
        def __init__(self, shape):
            self.__shape = shape

        def __len__(self):
            return self.__shape.length_count()

        def __iter__(self):
            return self.__shape.length_keys_iter()

        def __getitem__(self, key):
            return self.__shape.get_length(key)

    def get_point(self, key):
        """
        Returns the associated labeled `~pyps.geom.Point` object for this shape.

        Each class of shapes can provide a set of labeled points associated with each
        instance of that shape. For instance, a circle might have a point labeled ``'center'``
        to represent the center of the circle.

        This method provides access to those labeled points for this instance.

        The returned point is a dynamic `~pyps.geom.Point` which will always reflect
        the appropriate point based on the current state of the shape.

        The base implementation does not provide any labeled points, so this always
        raises a |KeyError|.
        """
        raise KeyError('No such point: %s' % (key,))

    def point_keys_iter(self):
        """
        Iterate over all the canonical keys that can be accepted by `get_point`.

        This is empty in the base class.
        """
        return iter([])

    def get_length(self, key):
        """
        Returns the associated labeled `~pyps.geom.Length` for this shape.

        This is similar to `get_length`, except instead of returning lengths, it returns
        some intrinsic length. For instance, a circle might have a length labeled as
        ``'radius'`` which is always equal to the radius of the circle.

        These should only be lengths that are **intrinsic** to the shape itself. For instance,
        distance between two specific lengths on the shape may be appropriate, but distance
        between this shape and the origin, or this shape and any other shape or length is
        _not_. The reason is that linear transformations will be applied to returned values,
        which is only appropriate for intrinsic lengths.

        The base class doesn't provide any labeled lengths, so this will always raise a |KeyError|.
        """
        raise KeyError('No such length: %s' % (key,))

    def length_keys_iter(self):
        """
        Iterator over all the canonical keys that can be accepted by `get_length`.

        This is empty in the base class.
        """
        return iter([])


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
        self._width = self._Width(self)
        self._height = self._Height(self)
        self._area = self._Area(self)
        self._center = self._Center(self)
        self._perimeter = self._Perimeter(self)
        self._diagonal = self._Diagonal(self)
        super(Box, self).__init__()

    def render(self, capabilities=[]):
        return [
            Path.moveTo(self.lowerleft),
            Path.lineTo(self.upperleft),
            Path.lineTo(self.upperright),
            Path.lineTo(self.lowerright),
            Path.close(),
        ]

    @ShapeMeta.point('c')
    def center(self):
        """
        A dynamic point representing the center of the box.
        """
        return self._center

    @ShapeMeta.point('ll', 'bl')
    def lowerleft(self):
        """
        Returns a dynamic point which represents the lower left corner of the box
        (minimum X and minimum Y).
        """
        return self._lowerleft

    @ShapeMeta.point('lr', 'br')
    def lowerright(self):
        """
        Returns a dynamic point which represents the lower right corner of the box
        (maximum X and minimum Y).
        """
        return self._lowerright

    @ShapeMeta.point('ul', 'tl')
    def upperleft(self):
        """
        Returns a dynamic point which represents the upper left corner of the box
        (minimum X and maximum Y).
        """
        return self._upperleft

    @ShapeMeta.point('ur', 'tr')
    def upperright(self):
        """
        Returns a dynamic point which represents the upper right corner of the box
        (maximum X and maximum Y).
        """
        return self._upperright

    @ShapeMeta.length('w')
    def width(self):
        """
        A dynamic `~geom.Length` representing the width of the box (horizontal extent).
        """
        return self._width

    @ShapeMeta.length('h')
    def height(self):
        """
        A dynamic `~geom.Length` representing the height of the box (vertical extent).
        """
        return self._height

    @ShapeMeta.length('d', 'diag')
    def diagonal(self):
        """
        A dynamic `~geom.Length` representing the length of either diagonal of the box.
        """
        return self._diagonal

    @ShapeMeta.length('perim')
    def perimeter(self):
        """
        A dynamic `~geom.Length` representing the perimeter of the box.
        """
        return self._perimeter


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
        """
        Returns the maximum Y coordinate of the box, based on `get_bounds`.
        """
        return self.get_bounds()[0]

    def get_south(self):
        """
        Returns the minimum Y coordinate of the box, based on `get_bounds`.
        """
        return self.get_bounds()[2]

    def get_east(self):
        """
        Returns the maximum X coordinate of the box, based on `get_bounds`.
        """
        return self.get_bounds()[1]

    def get_west(self):
        """
        Returns the minimum X coordinate of the box, based on `get_bounds`.
        """
        return self.get_bounds()[3]

    #TODO: Create dynamic Lengths for width and height, use them as labeled lengths with the @ShapeMeta.length decorator.

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

    def get_diagonal(self):
        """
        Returns the current length of either of the two diagonals of the box.
        """
        w = self.get_width()
        h = self.get_height()
        return math.sqrt(w*w + h*h)

    def get_perimeter(self):
        """
        Returns the current perimeter of the box.
        """
        w = self.get_width()
        h = self.get_height()
        return w + w + h + h

    def get_area(self):
        """
        Returns the current area of the box, the product of the `width <get_width>`
        and the `height <get_height>`.
        """
        return self.get_width() * self.get_height()

    @property
    def area(self):
        """
        A dynamic `~geom.Length` object representing the area of the box.
        """
        return self._area

    def hittest(self, x, y):
        n, e, s, w = self.get_bounds()
        return (w <= x <= e) and (s <= y <= n)

    @property
    def boundingbox(self):
        """
        The bounding box for a box is always itself.
        """
        return self

    def get_boundingpoly(self, quality=0.5):
        """
        The bounding poly for a box is always itself.
        """
        return self

    class _Length(geom.Length):
        def __init__(self, box):
            self._box = box

    class _Width(_Length):
        def get_float(self):
            return self._box.get_width()

    class _Height(_Length):
        def get_float(self):
            return self._box.get_height()

    class _Diagonal(_Length):
        def get_float(self):
            return self._box.get_diagonal()

    class _Perimeter(_Length):
        def get_float(self):
            return self._box.get_perimeter()

    class _Area(_Length):
        def get_float(self):
            return self._box.get_area()

    class _Corner(geom.Point):
        """
        Utility class to implement a dynamic `~pyps.geom.Point` representing a
        particular corner of a box. This is an abstract base class, you need to
        use one of the other concrete subclasses.
        """
        def __init__(self, box):
            self._box = box
            self._x = self._X(self)
            self._y = self._Y(self)
            super(Box._Corner, self).__init__()

        def get_coords(self):
            """
            Coordinates of the point come from the `get_x` and `get_y` abstract methods.
            """
            return (self.get_x(), self.get_y())

        @property
        def x(self):
            return self._x

        @property
        def y(self):
            return self._y
            
        @abc.abstractmethod
        def get_x(self):
            raise NotImplementedError()

        @abc.abstractmethod
        def get_y(self):
            raise NotImplementedError()

        class _Float(geom.Float):
            def __init__(self, corner):
                self._corner = corner
                super(Box._Corner._Float, self).__init__()

        class _X(_Float):
            def get_float(self):
                return self._corner.get_x()

        class _Y(_Float):
            def get_float(self):
                return self._corner.get_y()

    class _Center(_Corner):
        def get_x(self):
            n, e, s, w = self._box.get_bounds()
            return (e + w)*0.5

        def get_y(self):
            n, e, s, w = self._box.get_bounds()
            return (n + s)*0.5

        def get_coords(self):
            n, e, s, w = self._box.get_bounds()
            return ((e+w)*0.5, (n+s)*0.5)

    class _LeftCorner(_Corner):
        def get_x(self):
            return self._box.get_bounds()[3]

    class _RightCorner(_Corner):
        def get_x(self):
            return self._box.get_bounds()[1]

    class _UpperCorner(_Corner):
        def get_y(self):
            return self._box.get_bounds()[0]

    class _LowerCorner(_Corner):
        def get_y(self):
            return self._box.get_bounds()[2]

    class _LowerLeftCorner(_LeftCorner, _LowerCorner): pass
    class _LowerRightCorner(_RightCorner, _LowerCorner): pass
    class _UpperLeftCorner(_LeftCorner, _UpperCorner): pass
    class _UpperRightCorner(_RightCorner, _UpperCorner): pass



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
        super(Circle, self).__init__(**kwargs)
        self._center = geom.Point.cast(center, "Center must be a point: %r" % (center,))
        self._radius = geom.Length.cast(radius, "Radius must be a length: %r" % (radius,))
        self._bbox = self.BBox(self)

        nrad = geom.Negative(self._radius)
        self._north = geom.Translated(self._center, dy=self._radius)
        self._south = geom.Translated(self._center, dy=nrad)
        self._east = geom.Translated(self._center, dx=self._radius)
        self._west = geom.Translated(self._center, dx=nrad)
        self._diameter = geom.ProductLength(self._radius, 2.0)
        self._circumference = geom.ProductLength(self._radius, TAU)
        self._area = geom.ProductLength(self._radius, self._radius, math.pi)


    @ShapeMeta.point('c')
    def center(self):
        """
        The Point representing the center of the circle.
        """
        return self._center

    @ShapeMeta.point('n', 'up', 'u')
    def north(self):
        """
        The `Point` representing the northern-most point of the circle, which
        is the point with the greatest Y coordinate value.
        """
        return self._north

    @ShapeMeta.point('s', 'down', 'd')
    def south(self):
        """
        The `Point` representing the southern-most point of the circle, which
        is the point with the minimum Y coordinate value.
        """
        return self._south

    @ShapeMeta.point('e', 'right', 'r')
    def east(self):
        """
        The `Point` representing the eastern-most point of the circle, which
        is the point with the greatest X coordinate value.
        """
        return self._east

    @ShapeMeta.point('w', 'left', 'l')
    def west(self):
        """
        The `Point` representing the western-most point of the circle, which
        is the point with the minimum X coordinate value.
        """
        return self._west

    @ShapeMeta.length('r')
    def radius(self):
        """
        A `~pyps.geom.Length` representing the radius of the circle.
        """
        return self._radius

    @ShapeMeta.length('d', 'diam')
    def diameter(self):
        """
        A `~pyps.geom.Length` representing the diameter of the circle, which
        is twice the radius.
        """
        return self._diameter

    @ShapeMeta.length('c', 'circum', 'perimeter', 'perim')
    def circumference(self):
        """
        A `~pyps.geom.Length` representing the circumference of the circle,
        which is equal to 2*pi times the radius.
        """
        return self._circumference

    def get_radius(self):
        """
        Returns the current radius of the circle, as a float.
        """
        return float(self._radius)

    def get_diameter(self):
        """
        Returns the current diameter of the circle, as a float.
        """
        return float(self._diameter)

    def get_circumference(self):
        """
        Returns the current circumeference of the circle, as a float.
        """
        return float(self._circumference)

    @property
    def area(self):
        """
        A `~pyps.geom.Float` representing the area of the circle, which is
        pi times the square of the radius.
        """
        return self._area

    def get_area(self):
        """
        Returns the current area of the circle, as a float.
        """
        return float(self._area)

    def hittest(self, x, y):
        cx, cy = self._center.get_coords()
        r = self.get_radius()
        dx = cx - x
        dy = cy - y
        return (dx*dx + dy*dy) <= (r * r)

    @property
    def boundingbox(self):
        return self._bbox

    #TODO: get_boundingpoly.

    def render(self, capabilities=[]):
        return [Path(paint=self).circle(self._center, self._radius)]

    class BBox(Box):
        """
        Implements the `~Circle.boundingbox` for a `Circle`.
        """
        def __init__(self, circle):
            super(Circle.BBox, self).__init__()
            self._circle = circle
            self._diagonal = geom.ProductLength(TWO_RAD_TWO, circle.lengths['radius'])

        @ShapeMeta.length('d', 'diag')
        def diagonal(self):
            """
            We can calculate the diagonal of the bounding box more efficiently because
            we know it's a square.
            """
            return self._diagonal

        def get_diagonal(self):
            return float(self._diagonal)

        @ShapeMeta.point('c')
        def center(self):
            #We can do this more efficiently than the standard way.
            return self._circle._center

        def get_bounds(self):
            r = self._circle.get_radius()
            x, y = self._circle._center.get_coords()
            return (y+r, x+r, y-r, x-r)

