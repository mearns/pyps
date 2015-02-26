#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps import geom
from pyps.shapes import Shape, UnionBox

from docit import *

import types
import abc
import collections

class Transformation(Shape, collections.MutableMapping):
    """
    This is the base class for transformations. Each object acts as a container
    for any number of `~pyps.shapes.Shape` objects and acts as a local coordinate system
    for the contained shapes, which is transformed relative to the coordinate system
    of the container itself.
    """

    def __init__(self, *shapes, **keyed_shapes):
        self._box = self.Box(self)
        self.__shapes = {}
        self.add(*shapes, **keyed_shapes)

    def add(self, *shapes, **keyed_shapes):
        """
        Adds multiple shapes to the collection, with or without keys.

        Delegates to `add_shape`, but returns ``self`` for convenience.

        :param \*shapes: Any positional arguments are passed to `add_shape` without
            a ``key`` argument.

        :param \*\*keyed_shapes:    Any keyword arguments are passed to `add_shape`,
            using the keyword as the ``key``.

        """
        for shape in shapes:
            self.add_shape(shape)
        for k, v in keyed_shapes.iteritems():
            self.add_shape(v, k)

        return self

    def add_shape(self, shape, key=None):
        """
        Adds a new shape to the collection. If a key is given, it must be a string
        and can be used to retrieve the shape later. If a key is not given, a numeric
        key will be generated for it.

        In either case, the associated key is returned.

        If you specify an existing key, you will get a |KeyError|. If you want to replace
        an item, you need to delete the key from the collection first.
        """
        if not isinstance(shape, Shape):
            raise TypeError('Can only add Shape objects: %r' % (shape,))
        if key is None:
            key = len(self.__shapes)
        else:
            if not isinstance(key, types.StringTypes):
                raise TypeError('Key must be a string type: %r' % (key,))

        if key in self.__shapes:
            raise KeyError('Key already exists: %r' % (key,))
        self.__shapes[key] = shape

        return key

    @docit
    def __setitem__(self, key, value):
        """
        Delegate to `add_shape`.
        """
        self.add_shape(value, key)

    @docit
    def __delitem__(self, key):
        """
        Removes the item with the specified key from the collection.
        """
        del(self.__shapes[key])

    @docit
    def __len__(self):
        """
        The number of contained shapes.
        """
        return len(self.__shapes)

    @docit
    def __iter__(self):
        """
        Iterates over the keys for all contained shapes.
        """
        return iter(self.__shapes)

    @docit
    def __getitem__(self, key):
        """
        Retreive a contained shape by its key.
        """
        return self.__shapes[key]

    def itershapes(self):
        """
        Iterate over the contained `~pyps.shape.Shape` objects themselves.
        """
        return self.__shapes.itervalues()

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
        for shape in self.itershapes():
            if shape.hittest(x,y):
                return True
        return False

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

    @property
    def boundingbox(self):
        return self._box

    class Box(UnionBox):
        def __init__(self, xform):
            self._xform = xform

        def iterboxes(self):
            #FIXME: itershapes needs to iterate over the transformed shapes. Transformed shapes need to convert points, angles, and lengths.
            return s.boundingbox for s in self._xform.itershapes()
        

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
    
