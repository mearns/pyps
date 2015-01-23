#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:


import sys

if __name__ == '__main__':
    
    from writers.postscript import *

    writer = EPSWriter()
    with open('test_output.eps', 'wb') as ostream:
        writer.write(ostream)



