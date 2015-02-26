#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:


import sys

if __name__ == '__main__':
    
    import pyps
    from pyps.shapes import *


    c = Circle((5, 7), 3)
    print c.points['c']
    print c.points.c
    print c.points['center']
    print c.lengths.radius
    print list(c.lengths)

    box = c.boundingbox()
    print box.points.keys()
    print list(box.point_keys_iter())


