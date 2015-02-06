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

def test_complementary_angles():
    eq_(geom.ComplementaryAngle(0).get_float(), 90)
    eq_(geom.ComplementaryAngle(10).get_float(), 80)
    eq_(geom.ComplementaryAngle(80).get_float(), 10)
    eq_(geom.ComplementaryAngle(90).get_float(), 0)
    eq_(geom.ComplementaryAngle(-10).get_float(), 10)
    eq_(geom.ComplementaryAngle(200).get_float(), 70)
    eq_(geom.ComplementaryAngle(500).get_float(), 40)
    eq_(geom.ComplementaryAngle(-200).get_float(), 20)

def test_suplimentary_angles():
    eq_(geom.SupplementaryAngle(0).get_float(), 180.0)
    eq_(geom.SupplementaryAngle(10).get_float(), 170.0)
    eq_(geom.SupplementaryAngle(170).get_float(), 10.0)
    eq_(geom.SupplementaryAngle(180).get_float(), 0.0)
    eq_(geom.SupplementaryAngle(360).get_float(), 0.0)
    eq_(geom.SupplementaryAngle(270).get_float(), 90.0)
    eq_(geom.SupplementaryAngle(400).get_float(), 140.0)
    eq_(geom.SupplementaryAngle(500).get_float(), 40.0)
    eq_(geom.SupplementaryAngle(-180).get_float(), 0.0)
    eq_(geom.SupplementaryAngle(-170).get_float(), 170.0)
    eq_(geom.SupplementaryAngle(-270).get_float(), 90.0)
    eq_(geom.SupplementaryAngle(-300).get_float(), 120.0)

def test_reflex_angles():
    eq_(geom.ReflexAngle(0).get_float(), 360.0)
    eq_(geom.ReflexAngle(360).get_float(), 0.0)
    eq_(geom.ReflexAngle(180).get_float(), 180.0)
    eq_(geom.ReflexAngle(-180).get_float(), 180.0)
    eq_(geom.ReflexAngle(90).get_float(), 270.0)
    eq_(geom.ReflexAngle(80).get_float(), 280.0)
    eq_(geom.ReflexAngle(-90).get_float(), 90.0)
    eq_(geom.ReflexAngle(400).get_float(), 320.0)
    eq_(geom.ReflexAngle(500).get_float(), 220.0)
    eq_(geom.ReflexAngle(720).get_float(), 0.0)
    eq_(geom.ReflexAngle(-360).get_float(), 360.0)
    eq_(geom.ReflexAngle(-200).get_float(), 200.0)
    eq_(geom.ReflexAngle(-400).get_float(), 40.0)

def test_abs():
    def eval(val, expected):
        absv = geom.Abs(val)
        eq_(absv.get_float(), expected)
        ok_(isinstance(absv, geom.Length))

    eval(400, 400)
    eval(-400, 400)
    eval(-314.159, 314.159)
    eval(geom.Sum(45, -100), 55)
    eval(geom.Difference(111, 986), 875)
    

