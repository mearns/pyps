#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

import abc
import collections
import colour

class Color(object):

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def cast(other, error_message=None):
        """
        Attempts to cast the given object to an instance of `Color`.

        If ``other`` is already a `Color`, then it is returned.

        Otherwise, if ``other`` is a sequence of three or four numbers, they
        are passed as positional arguments to `FixedColor`, and the created
        instance is returned.

        :param other:   The object to cast to a `Color`.

        :param error_message:   Optional, if given, this is used as the error message
            if a |TypeError| is generated.

        :raises TypeError:  If ``other`` is not castable to a `Color`.
        """

        if isinstance(other, Color):
            return other
        elif isinstance(other, collections.Sequence):
            if len(other) in (3, 4):
                return FixedColor(*other)
        
        raise TypeError(error_message or ('Could not cast to Color: %r' % (other,)))

    @staticmethod
    def Fixed(*args, **kwargs):
        """
        Generates an instance of `FixedColor` using the same parameters as `colour.Color`.
        """
        return FixedColor(*(colour.Color(*args, **kwargs).rgb))

    @staticmethod
    def cast_or_none(other, error_message=None):
        if other is None:
            return other
        return Color.cast(other, error_message)


    @abc.abstractmethod
    def rgbf(self):
        """
        Returns the color in the RGB color space as a tuple :samp:`({r}, {g}, {b})`,
        with normalized values so each of the red, green, and blue components
        have a maximum vaue of 1.0 and a minimum value of 0.0.
        """
        raise NotImplementedError()


class FixedColor(Color):


    def __init__(self, r, g, b, divisor=1.0):
        divisor = float(divisor)
        self._r = float(r) / divisor
        self._g = float(g) / divisor
        self._b = float(b) / divisor

        if not all (0.0 <= c <= 1.0 for c in (self._r, self._g, self._b)):
            raise ValueError("RGB Value must have normalized values between 0 and 1.")

    def rgbf(self):
        return (self._r, self._g, self._b)

