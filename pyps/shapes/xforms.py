#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps import geom
from pyps.shapes import Shape, UnionBox, Box, Path

from docit import *

import types
import abc
import collections


class Transformation(object):
    """
    This is the base class for transformations. Each object acts as a container
    for any number of `~pyps.shapes.Shape` objects and acts as a local coordinate system
    for the contained shapes, which is transformed relative to the coordinate system
    of the container itself.

    Concrete subclasses must implement `to_local` and `to_global` to traslate between
    the local and global coordinate systems.
    """

    def __init__(self):
        super(Transformation, self).__init__()
        self._box = self.Box(self)

    @property
    def boundingbox(self):
        return self._box

    @abc.abstractmethod
    def length_to_global(self, length):
        return length

    @abc.abstractmethod
    def point_to_global(self, pt):
        return pt

    @abc.abstractmethod
    def render_local(self, paths, capabilities=[]):
        raise NotImplementedError()

    def transform(self, *shapes):
        shapes = [self.Transform(self, shape) for shape in shapes]
        if len(shapes) == 1:
            return shapes[0]
        return shapes

    def render(self, capabilities=[]):
        paths = sum(s.render(capabilities) for s in self.itershapes())
        return self.render_local(paths, capabilities)

    def hittest(self, x, y):
        """
        Hittest simply delegates to all of the contained shapes. If any of them hit,
        then the container hits.

        The given point is in the parent ("global") coordinate space, but it will
        be translated to the local coordinate space when doing the hittest on the
        contained shapes, since those shapes operate entirely in the local coordinate
        space.
        """
        x, y = self.to_local(geom.FixedPoint(x, y)).get_coords()
        return super(Transformation, self).hittest(x, y)


    class Box(UnionBox):
        def __init__(self, xform):
            self._xform = xform

        def iterboxes(self):
            #FIXME: itershapes needs to iterate over the transformed shapes. Transformed shapes need to convert points, angles, and lengths.
            return (s.boundingbox for s in self._xform.itershapes())

    class Transform(Shape):
        """
        Represents the results of applying the group's transformation to a specific shape.
        """
        def __init__(self, group, shape):
            super(Transformation.Transform, self).__init__()
            self._group = group
            self._shape = shape
            self._bbox = self._BBox(self)

        def point_count(self):
            return self._shape.point_count()

        def point_keys_iter(self):
            return self._shape.point_keys_iter()

        def get_point(self, key):
            return self._group.point_to_global(self._shape.get_point(key))

        def length_count(self):
            return self._shape.length_count()

        def length_keys_iter(self):
            return self._shape.length_keys_iter()

        def get_length(self, key):
            return self._group.length_to_global(self._shape.get_length(key))

        def hittest(self, x, y):
            x, y = self._group.point_to_local(geom.FixedPoint(x, y)).get_coords()
            return self._shape.hittest(x, y)

        def render(self, capabilities=[]):
            return self._group.render_local(self._shape.render(capabilities), capabilities)

        @property
        def boundingbox(self):
            return self._bbox

        def get_boundingpoly(self):
            #TODO: for get_boundingpoly, if complexity is 0, return self._bbox, otherwise need to get the polygon from the shape, and transform all the points on it.
            return self._bbox

        class _BBox(Box):
            def __init__(self, xform):
                super(Transformation.Transform._BBox, self).__init__()
                self._xform = xform

            def get_bounds(self):
                #TODO: This class could probably be improved significantly by implementing custom objects for each of the corners.
                n, e, s, w = self._xform._shape.boundingbox.get_bounds()
                ne = self._xform._group.point_to_global(geom.FixedPoint(e, n))
                nw = self._xform._group.point_to_global(geom.FixedPoint(w, n))
                se = self._xform._group.point_to_global(geom.FixedPoint(e, s))
                sw = self._xform._group.point_to_global(geom.FixedPoint(w, s))
                points = [ne, nw, se, sw]
                ys = sorted([pt.get_y() for pt in points])
                xs = sorted([pt.get_x() for pt in points])
                return ys[3], xs[3], ys[0], xs[0]
                
class Translation(Transformation):
    def __init__(self, dx=0, dy=0):
        super(Translation, self).__init__()
        self._dx = geom.Float.cast(dx)
        self._dy = geom.Float.cast(dy)
    
    def length_to_global(self, length):
        return length

    def point_to_global(self, pt):
        return pt.translate(self._dx, self._dy)

    @abc.abstractmethod
    def render_local(self, paths, capabilities=[]):
        return [Path().translation(self._dx, self._dy, paths)]


