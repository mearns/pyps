#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:


import sys

if __name__ == '__main__':
    
    import pyps
    from pyps.writers.postscript import *
    from pyps.shapes import *
    import subprocess

    doc = pyps.Document()

    doc.add_shape(Circle((100, 100), 50))

    writer = EPSWriter()
    with open('test_output.eps', 'wb') as ostream:
        writer.write(ostream, doc)


    subprocess.check_call(['convert', 'test_output.eps', 'test_output.png'], shell=True)



