#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from nose.tools import *
import math

from pyps import geom

def test_sum():
    eq_(geom.Sum(15, 12).get_float(), 27)
    eq_(geom.Sum(15, -12).get_float(), 3)
    eq_(geom.Sum(-15, -12).get_float(), -27)
    eq_(geom.Sum(geom.Sum(10, 5), geom.Sum(-3, 15)).get_float(), 27)

def test_sum_angle():
    eq_(geom.SumAngle(15, 12).get_float(), 27)
    eq_(geom.SumAngle(15, 12, -17).get_float(), 10)
    eq_(geom.SumAngle(15, -12).get_float(), 3)
    eq_(geom.SumAngle(-15, -12).get_float(), -27)
    eq_(geom.SumAngle(geom.SumAngle(10, 5), geom.SumAngle(-3, 15)).get_float(), 27)
    eq_(geom.SumAngle(geom.Sum(10, 10), geom.SumAngle(10, 15)).get_radians(), math.pi/4.0)

def test_sum_length():
    eq_(geom.SumLength(15, 12).get_float(), 27)
    eq_(geom.SumLength(15, 12, 10).get_float(), 37)
    eq_(geom.SumLength(geom.SumLength(10, 5), 12).get_float(), 27)

    @raises(ValueError)
    def make_sum(a, b):
        return geom.SumLength(a, b)

    make_sum(15, -12)
    make_sum(-15, 12)
    make_sum(-15, -12)


def test_mean():
    eq_(geom.Mean(10, 20, 30, 40, 50, 60).get_float(), 35)
    

