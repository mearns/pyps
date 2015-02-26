#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:


import sys

if __name__ == '__main__':
    
    import pyps
    from pyps.shapes import *
    from pyps.shapes.xforms import *
    from pyps.writers.postscript import EPSWriter
    import subprocess

    doc = pyps.Document()
    c = Circle((100, 200), 50)

    xf = Translation(300, 100)
    g = TransformationGroup(xf, c)

    doc.add_shape(Painted(c.boundingbox, fill=(1, 0, 0)))
    doc.add_shape(Painted(g.boundingbox, fill=(1, 1, 0)))
    doc.add_shape(g)
    doc.add_shape(c)


    writer = EPSWriter()
    ofile = 'test_output.eps'
    with open(ofile, 'wb') as ostream:
        writer.write(ostream, doc, True)


    subprocess.check_call(['convert', ofile, 'test_output.png'], shell=True)

