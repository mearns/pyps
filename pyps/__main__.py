#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:


import sys

if __name__ == '__main__':
    
    import pyps
    from pyps.writers.postscript import *
    from pyps.shapes import *
    import subprocess

    doc = pyps.Document()

    doc.add_shape(Circle((100, 100), 50, title="My Circle", fill=(255, 128, 50)))
    doc.add_shape(Circle((150, 100), 30, title="My Circle"))

    writer = EPSWriter()
    with open('test_output.eps', 'wb') as ostream:
        writer.write(ostream, doc, verbose=True)


    subprocess.check_call(['convert', 'test_output.eps', 'test_output.png'], shell=True)



