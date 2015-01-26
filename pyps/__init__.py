#! /usr/bin/env python
# vim: set fileencoding=utf-8: 

"""
The toplevel module for the pyps package.
"""

import abc

from docit import *

from pyps import shapes

class Document(object):
    def __init__(self):
        self.__shapes = []

    def add_shape(self, *shapes):
        not_shapes = filter(lambda s : not isinstance(s, shapes.Shape), shapes)
        if not_shapes:
            raise TypeError('Only Shapes can be added to a Document: %s' % (', '.join(repr(s) for s in not_shapes)))
        self.__shapes.extend(shapes)

    def get_shapes(self):
        return tuple(self.__shapes)

    def shape_count(self):
        return len(self.__shapes)

    def get_shape(self, idx):
        return self.__shapes[idx]

    def itershapes(self):
        return iter(self.__shapes)

