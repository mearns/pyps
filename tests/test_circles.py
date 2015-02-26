#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps.shapes import Circle
from pyps.geom import Length
from pyps.geom import Point

from nose.tools import *

import math

def test_lengths():
    c = Circle((3, 4), 7)

    expected_names = dict(
        radius = ['r'],
        diameter = ['d', 'diam'],
        circumference = ['c', 'circum', 'perim', 'perimeter'],
    )

    eq_(float(c.lengths['radius']), 7)
    eq_(float(c.lengths['diameter']), 14)
    eq_(float(c.lengths['circumference']), 14*math.pi)

    #Make sure the set of keys contains all of the expected keys.
    ok_(set(expected_names.keys()) <= set(c.lengths.keys()), c.lengths.keys())

    #Make sure the two main ways of accessing the canonical keys agree.
    eq_(set(c.lengths.keys()), set(c.length_keys_iter()))

    for name, aliases in expected_names.iteritems():
        ok_(name in c.lengths, "Missing %s" % name)
        length = c.lengths[name]
        ok_(isinstance(length, Length), type(length))
        ok_(hasattr(c.lengths, name))
        eq_(length, getattr(c.lengths, name))

        for alias in aliases:
            ok_(alias in c.lengths, "Missing alias %s" % alias)
            alength = c.lengths[alias]
            eq_(alength, length)
            ok_(hasattr(c.lengths, alias))
            eq_(alength, getattr(c.lengths, alias))



def test_points():
    c = Circle((3, 4), 7)

    expected_names = dict(
        center = ['c'],
        north = ['n', 'up', 'u'],
        south = ['s', 'down', 'd'],
        east = ['e', 'right', 'r'],
        west = ['w', 'left', 'l'],
    )

    ok_(c.points['center'].is_at(3, 4))
    ok_(c.points['north'].is_at(3, 11))
    ok_(c.points['south'].is_at(3, -3))
    ok_(c.points['east'].is_at(10, 4))
    ok_(c.points['west'].is_at(-4, 4))

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

