#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:


import sys

if __name__ == '__main__':
    
    import pyps
    from pyps.writers.postscript import *
    from pyps.shapes import *
    from pyps.art.color import Color
    import subprocess

    doc = pyps.Document()

    doc.add_shape(Circle(
        (100, 100), 50,
        title="My Circle",
        fill=Color.Fixed(red=0.2, green=0.5, blue=1.0),
        stroke=Color.Fixed('#66ff99'),
        stroke_width=5)
    )
    doc.add_shape(Circle((150, 100), 30, title="My Circle", stroke=(255, 0, 0, 255), stroke_width=3))

    writer = EPSWriter()
    with open('test_output.eps', 'wb') as ostream:
        writer.write(ostream, doc, verbose=True)

    subprocess.check_call(['convert', 'test_output.eps', 'test_output.png'], shell=True)



