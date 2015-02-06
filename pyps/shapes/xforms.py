#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps.shapes import Shape 

from pyps import geom

class Translate(Shape):

    def __init__(self, dx, dy, shape):
        self._dx = geom.Length.cast(dx, "Translation dx must be a length.")
        self._dy = geom.Length.cast(dy, "Translation dy must be a length.")

        if not isinstance(shape, Shape):
            raise TypeError('Translation can only be applied to a Shape: %r' % (shape,))
        self._shape = shape

        super(Translate, self).__init__()

    def to_local(self, x, y):
        return (x - self.dx, y - self.dy)

    def to_global(self, pt):
        return geom.Point.cast(pt).translate(self._dx, self._dy)

    def hittest(self, x, y):
        return self._shape.hittest(*(self.to_local(x,y)))

    def boundingbox(self):
        #FIXME XXX: Need to dynamically translate, because as the wrapped shape changes, lowerleft Point object may not stay the same.
        return BoundingBox(lowerleft, upperright)

    def boundingpoly(self, complexity=0.5):
        #TODO: Implement
        pass

    def render(self, capabilities=[]):
        #TODO: Implement
        pass

