#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps.shapes import Circle
from pyps.geom import Length
from pyps.geom import Point

from nose.tools import *

import math

def test_area():
    c = Circle((3, 4), 7)

    eq_(float(c.area), math.pi*49)
    eq_(float(c.area), c.get_area())

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


def test_pt_move():
    center = Point.cast((3, 4))
    uut = Circle(center, 7)

    ok_(uut.points['center'] is center)

    ok_(uut.points['center'].is_at(3, 4))
    ok_(uut.points['north'].is_at(3, 11))
    ok_(uut.points['south'].is_at(3, -3))
    ok_(uut.points['east'].is_at(10, 4))
    ok_(uut.points['west'].is_at(-4, 4))

    center.moveTo(9, 5)
    ok_(uut.points['center'] is center)
    ok_(uut.points['center'].is_at(9, 5))
    ok_(uut.points['north'].is_at(9, 12), str(uut.points['north']))
    ok_(uut.points['south'].is_at(9, -2))
    ok_(uut.points['east'].is_at(16, 5))
    ok_(uut.points['west'].is_at(2, 5))


def test_radius_change():
    uut = Circle((3, 4), 7)

    rad = uut.lengths.r
    diam = uut.lengths.d
    circum = uut.lengths.c
    area = uut.area
    n = uut.points.n
    e = uut.points.e
    s = uut.points.s
    w = uut.points.w
    c = uut.points.c

    eq_(uut.get_radius(), 7)
    eq_(uut.get_diameter(), 14)
    eq_(uut.get_circumference(), 14*math.pi)
    eq_(uut.get_area(), 49*math.pi)
    ok_(uut.points['center'].is_at(3, 4))
    ok_(uut.points['north'].is_at(3, 11))
    ok_(uut.points['south'].is_at(3, -3))
    ok_(uut.points['east'].is_at(10, 4))
    ok_(uut.points['west'].is_at(-4, 4))
    eq_(uut.get_radius(), float(rad))
    eq_(uut.get_diameter(), float(diam))
    eq_(uut.get_circumference(), float(circum))
    eq_(uut.get_area(), float(area))
    eq_(uut.points['center'].get_coords(), c.get_coords())
    eq_(uut.points['north'].get_coords(), n.get_coords())
    eq_(uut.points['east'].get_coords(), e.get_coords())
    eq_(uut.points['south'].get_coords(), s.get_coords())
    eq_(uut.points['west'].get_coords(), w.get_coords())


    rad.set(3)
    eq_(uut.get_radius(), 3)
    eq_(uut.get_diameter(), 6)
    eq_(uut.get_circumference(), 6*math.pi)
    eq_(uut.get_area(), 9*math.pi)
    ok_(uut.points['center'].is_at(3, 4))
    ok_(uut.points['north'].is_at(3, 7))
    ok_(uut.points['south'].is_at(3, 1))
    ok_(uut.points['east'].is_at(6, 4))
    ok_(uut.points['west'].is_at(0, 4))
    eq_(uut.get_radius(), float(rad))
    eq_(uut.get_diameter(), float(diam))
    eq_(uut.get_circumference(), float(circum))
    eq_(uut.get_area(), float(area))
    eq_(uut.points['center'].get_coords(), c.get_coords())
    eq_(uut.points['north'].get_coords(), n.get_coords())
    eq_(uut.points['east'].get_coords(), e.get_coords())
    eq_(uut.points['south'].get_coords(), s.get_coords())
    eq_(uut.points['west'].get_coords(), w.get_coords())




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


def test_bbox():

    c = Circle((3,4), 7)
    uut = c.boundingbox
    area = uut.area

    eq_(uut.get_area(), 14*14)
    eq_(float(area), uut.get_area())

