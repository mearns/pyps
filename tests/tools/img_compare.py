#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from PIL import ImageFilter
import math

def similar(im1, im2):
    """
    Checks to see if two images are "similar", which is very vaguely defined.
    """

    size = im1.size
    if im2.size != size:
        return False

    r = int(math.ceil(min(size) * 0.10))

    pix1 = im1.convert('RGB').filter(ImageFilter.GaussianBlur(r)).load()
    pix2 = im2.convert('RGB').filter(ImageFilter.GaussianBlur(r)).load()

    wrange = range(size[0])
    hrange = range(size[1])

    energy = 0
    for x in wrange:
        for y in hrange:
            loc = (x,y)
            rgb1 = pix1[loc]
            rgb2 = pix2[loc]
            if rgb1 != rgb2:
                deltas = [abs(rgb1[i]-rgb2[i]) for i in (0,1,2)]
                energy += sum(d*d for d in deltas)

    avg_energy = math.sqrt(float(energy) / float(3*size[0]*size[1]))
    print avg_energy
    return avg_energy < 6


