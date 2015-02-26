#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps.shapes import Circle
from pyps.geom import Point

from nose.tools import *

def test_circle_names():
    c = Circle((3, 4), 7)

    expected_names = dict(
        center = ['c'],
    )

    eq_(c.points['center'], (3, 4))

    #Make sure the set of keys contains all of the expected keys.
    ok_(set(expected_names.keys()) <= set(c.points.keys()), c.points.keys())

    #Make sure the two main ways of accessing the canonical keys agree.
    eq_(set(c.points.keys()), set(c.point_keys_iter()))

    for name, aliases in expected_names.iteritems():
        ok_(name in c.points, "Missing %s" % name)
        pt = c.points[name]
        ok_(isinstance(pt, Point), type(pt))
        ok_(hasattr(c.points, name))
        eq_(pt, getattr(c.points, name))

        for alias in aliases:
            ok_(alias in c.points, "Missing alias %s" % alias)
            apt = c.points[alias]
            eq_(apt, pt)
            ok_(hasattr(c.points, alias))
            eq_(apt, getattr(c.points, alias))

