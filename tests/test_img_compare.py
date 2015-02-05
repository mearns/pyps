#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from nose.tools import *
import os.path
import random
from PIL import Image, ImageDraw, ImageFilter

from tools import img_compare


def _load_test_image():
    image_path = os.path.join(os.path.dirname(__file__), 'res', 'test_image_small.png')
    return Image.open(image_path)

def _load_large_test_image():
    image_path = os.path.join(os.path.dirname(__file__), 'res', 'test_image.png')
    return Image.open(image_path)

def _add_noise(im, pct=0.1):
    def visitor(x, y, rgb):
        r, g, b = rgb
        if random.random() <= pct:
            return tuple(int(random.uniform(0, 255)) for i in (1,2,3))
        return rgb

    _visit_pixels(im, visitor)
            
def _test_noisy_compare(pct, expected_pass=True):
    im1 = _load_test_image()

    random.seed(31415926)
    seeds = [random.uniform(0, 65536) for i in range(10)]
    for seed in seeds:
        random.seed(seed)
        im2 = im1.copy()
        _add_noise(im2, pct)
        
        if expected_pass:
            ok_(img_compare.similar(im1, im2), "Images are not similar.")
        else:
            ok_(not img_compare.similar(im1, im2), "Images are similar.")

    

def _visit_pixels(im, func):
    pix = im.load()
    size = im.size
    wrange = range(size[0])
    hrange = range(size[1])
    for x in wrange:
        for y in hrange:
            pix[x,y] = func(x, y, pix[x,y])


def test_identical_images():
    im1 = _load_test_image()
    im2 = im1.copy()

    ok_(img_compare.similar(im1, im2), "Images are not similar")

def test_rotated_images():
    im1 = _load_test_image()
    im2 = im1.rotate(180)
    
    ok_(not img_compare.similar(im1, im2), "Images are similar")

def test_images_with_noise_01pct():
    _test_noisy_compare(0.01, True)

def test_images_with_noise_15pct():
    _test_noisy_compare(0.15, False)

def test_images_with_noise_25pct():
    _test_noisy_compare(0.25, False)

def test_images_with_noise_50pct():
    _test_noisy_compare(0.50, False)

def test_small_offset_h():
    im1 = _load_test_image()
    im2 = im1.copy()

    pix = im2.load()
    size = im2.size
    wrange = range(size[0]-1)
    hrange = range(size[1])
    for x in wrange:
        for y in hrange:
            pix[x,y] = pix[x+1,y]

    ok_(img_compare.similar(im1, im2), "Images are not similar.")

def test_large_offset_h():
    im1 = _load_test_image()
    im2 = im1.copy()

    pix = im2.load()
    size = im2.size
    wrange = range(size[0]-5)
    hrange = range(size[1])
    for x in wrange:
        for y in hrange:
            pix[x,y] = pix[x+5,y]

    ok_(not img_compare.similar(im1, im2), "Images are similar.")

def test_small_offset_v():
    im1 = _load_test_image()
    im2 = im1.copy()

    pix = im2.load()
    size = im2.size
    wrange = range(size[0])
    hrange = range(size[1]-1)
    for x in wrange:
        for y in hrange:
            pix[x,y] = pix[x,y+1]

    ok_(img_compare.similar(im1, im2), "Images are not similar.")

def test_large_offset_v():
    im1 = _load_test_image()
    im2 = im1.copy()

    pix = im2.load()
    size = im2.size
    wrange = range(size[0])
    hrange = range(size[1]-5)
    for x in wrange:
        for y in hrange:
            pix[x,y] = pix[x,y+5]

    ok_(not img_compare.similar(im1, im2), "Images are similar.")

def test_small_offset_hv():
    im1 = _load_test_image()
    im2 = im1.copy()

    pix = im2.load()
    size = im2.size
    wrange = range(size[0]-1)
    hrange = range(size[1]-1)
    for x in wrange:
        for y in hrange:
            pix[x,y] = pix[x+1,y+1]

    ok_(img_compare.similar(im1, im2), "Images are not similar.")

def test_large_offset_hv():
    im1 = _load_test_image()
    im2 = im1.copy()

    pix = im2.load()
    size = im2.size
    wrange = range(size[0]-3)
    hrange = range(size[1]-3)
    for x in wrange:
        for y in hrange:
            pix[x,y] = pix[x+3,y+3]

    ok_(not img_compare.similar(im1, im2), "Images are similar.")

def test_blurred_images():
    im1 = _load_test_image()
    im2 = im1.filter(ImageFilter.GaussianBlur(5))

    ok_(img_compare.similar(im1, im2), "Images are not similar.")

def test_heavily_blurred_images():
    im1 = _load_test_image()
    im2 = im1.filter(ImageFilter.GaussianBlur(50))

    ok_(not img_compare.similar(im1, im2), "Images are similar.")


