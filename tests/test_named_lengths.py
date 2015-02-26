#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps.shapes import Circle
from pyps.geom import Length

from nose.tools import *

import math

def test_circle():
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

