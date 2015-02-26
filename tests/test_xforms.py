#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from nose.tools import *

from PIL import Image

import tempfile

from tools import img_compare

from pyps.writers.postscript import EPSWriter
import subprocess
import os

import pyps
from pyps.shapes import Circle
from pyps.shapes import xforms


def _doc_to_img(doc):
    
    writer = EPSWriter()

    eps_fd, eps_file = tempfile.mkstemp('.eps', 'pyps_tests_')
    try:
        with os.fdopen(eps_fd, 'wb') as ostream:
            writer.write(ostream, doc)

        png_fd, png_file = tempfile.mkstemp('.png', 'pyps_test_')
        try:
            os.close(png_fd)

            subprocess.check_call(['convert', eps_file, png_file], shell=True)

            im = Image.open(png_file)
            im = im.convert('RGBA')
            im = im.convert('RGB')
            im.load()
            return im

        finally:
            try: os.close(png_fd)
            except: pass
            os.unlink(png_file)
    finally:
        try: os.close(eps_fd)
        except: pass
        os.unlink(eps_file)

def _test_docs_similar(doc1, doc2):
    im1 = _doc_to_img(doc1)
    im2 = _doc_to_img(doc2)

    ok_(img_compare.similar(im1, im2))

def test_translation():
    pass
