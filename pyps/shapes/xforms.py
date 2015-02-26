#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps import geom
from pyps.shapes import Shape, Group, UnionBox, Box, Path

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

    @abc.abstractmethod
    def length_to_global(self, length):
        return length

    @abc.abstractmethod
    def length_to_local(self, length):
        return length

    @abc.abstractmethod
    def point_to_global(self, pt):
        return pt

    @abc.abstractmethod
    def point_to_local(self, pt):
        return pt

    @abc.abstractmethod
    def render_local(self, paths, capabilities=[]):
        """
        Given a sequence of paths from the local coordinate space, render it in the
        global coordinate space.
        """
        raise NotImplementedError()

    def transform(self, *shapes):
        """
        Returns a new instance of `Transform` for this transformation and the given 
        shapes.

        If only one ``shape`` is given, returns a scalar value, the Transform for that
        shape. Otherwise, returns a sequence of Transforms for the given shapes.
        """
        shapes = [self.Transform(self, shape) for shape in shapes]
        if len(shapes) == 1:
            return shapes[0]
        return shapes

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
                

class TransformationGroup(Group):
    def __init__(self, transformation, *shapes, **keyed_shapes):
        self._transformation = transformation
        self._xforms = {}
        self._box = self.Box(self)
        super(TransformationGroup, self).__init__(*shapes, **keyed_shapes)

    def add_shape(self, shape, key=None):
        key = super(TransformationGroup, self).add_shape(shape, key)
        self._xforms[key] = self._transformation.transform(shape)
        return key

    def delete_shape(self, key):
        super(TransformationGroup, self).delete_shape(key)
        del(self._xforms[key])

    def get_transform(self, key):
        """
        Returns the `Transformation.Transform` object associated with the shape which
        has the given key in this collection. This object lives in the "global" (outer)
        coordinate space.
        """
        return self._xforms[key]

    def render(self, capabilities=[]):
        paths = sum((s.render(capabilities) for s in self.itershapes()), [])
        return self._transformation.render_local(paths, capabilities)

    def hittest(self, x, y):
        """
        Hittest simply delegates to all of the contained shapes. If any of them hit,
        then the container hits.

        The given point is in the parent ("global") coordinate space, but it will
        be translated to the local coordinate space when doing the hittest on the
        contained shapes, since those shapes operate entirely in the local coordinate
        space.
        """
        x, y = self.transformation.to_local(geom.FixedPoint(x, y)).get_coords()
        return super(TransformationGroup, self).hittest(x, y)

    def itertransforms(self):
        return (self.get_transform(k) for k in self)

    @property
    def boundingbox(self):
        return self._box

    def boundingpoly(self, complexity=0.5):
        #TODO: Can take the bounding poly from the super class (Group) and transform all the points.
        return self._box

    class Box(UnionBox):
        def __init__(self, xform):
            super(TransformationGroup.Box, self).__init__()
            self._xform = xform

        def iterboxes(self):
            #FIXME: itershapes needs to iterate over the transformed shapes. Transformed shapes need to convert points, angles, and lengths.
            return (s.boundingbox for s in self._xform.itertransforms())


class Translation(Transformation):
    def __init__(self, dx=0, dy=0):
        super(Translation, self).__init__()
        self._dx = geom.Float.cast(dx)
        self._dy = geom.Float.cast(dy)
        self._ndx = geom.Negative(self._dx)
        self._ndy = geom.Negative(self._dy)
    
    def length_to_global(self, length):
        return length
    
    def length_to_local(self, length):
        return length

    def point_to_global(self, pt):
        return pt.translate(self._dx, self._dy)

    def point_to_local(self, pt):
        return pt.translate(self._ndx, self._ndy)

    def render_local(self, paths, capabilities=[]):
        return [Path().translation(self._dx, self._dy, paths)]


