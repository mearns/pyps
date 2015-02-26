#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps.shapes import Circle, Group

from nose.tools import *


def test_union_001():
    c1 = Circle((0, 0), 1)
    c2 = Circle((2, 0), 1)
    uut = Group(c1, c2)

    bbox = uut.boundingbox
    eq_(bbox.get_width(), 4)
    eq_(bbox.get_height(), 2)
    eq_(bbox.points.ll.get_coords(), (-1, -1))
    eq_(bbox.points.lr.get_coords(), (3, -1))
    eq_(bbox.points.ul.get_coords(), (-1, 1))
    eq_(bbox.points.ur.get_coords(), (3, 1))

    ok_(uut.hittest(0, 0))
    ok_(uut.hittest(1, 0))
    ok_(uut.hittest(-1, 0))
    ok_(uut.hittest(0, 1))
    ok_(uut.hittest(0, -1))

    ok_(uut.hittest(2, 0))
    ok_(uut.hittest(3, 0))
    ok_(uut.hittest(2, 1))
    ok_(uut.hittest(2, -1))

    ok_(not uut.hittest(-0.9, 0.9))
    ok_(not uut.hittest(-0.9, -0.9))
    ok_(not uut.hittest(0.9, 0.9))
    ok_(not uut.hittest(0.9, -0.9))
    ok_(not uut.hittest(2.9, 0.9))
    ok_(not uut.hittest(2.9, -0.9))

    #Move one of the contained shapes.

    c2.points.center.moveTo(2, 2)

    eq_(bbox.get_width(), 4)
    eq_(bbox.get_height(), 4)
    eq_(bbox.points.ll.get_coords(), (-1, -1))
    eq_(bbox.points.lr.get_coords(), (3, -1))
    eq_(bbox.points.ul.get_coords(), (-1, 3))
    eq_(bbox.points.ur.get_coords(), (3, 3))

    ok_(uut.hittest(0, 0))
    ok_(uut.hittest(1, 0))
    ok_(uut.hittest(-1, 0))
    ok_(uut.hittest(0, 1))
    ok_(uut.hittest(0, -1))

    ok_(uut.hittest(2, 2))
    ok_(uut.hittest(3, 2))
    ok_(uut.hittest(2, 3))
    ok_(uut.hittest(2, 1))

    ok_(not uut.hittest(2, 0))
    ok_(not uut.hittest(3, 3))
    ok_(not uut.hittest(1, 1))


