#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from .. import Shape

class Circle(Shape):

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

