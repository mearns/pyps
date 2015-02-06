General Concepts
===================

Static and Dynamic Values
--------------------------

|PYPS| is designed to be dynamically adaptive. For instance, instead of
specifying the coordinates of the center of circle with a pair of numbers, you
can specify it to be the upper left corner of a particular rectangle, which
itself may be specified based on points from other shapes.

The important thing to realize is that when you use these mechanisms, you're
not simply copying a pair of numbers out of one point and into another, you're
actually creating a dynamic relationship between two points, so that if the
original point moves, the derived point moves as well in order to maintain the
relationship. This allows your code to be more flexible, and also makes it
much easier to modify a drawing live, or create several variants of a drawing
(for instance, frames in an animation).

It isn't just points that can be dynamically defined: lengths and angles can
be as well, and consequently `Shapes <pyps.shapes.Shape>` of all kinds. For
instance, lengths can be defined as the distance between two points, or the
difference between to other lengths, etc. Similarly with angles. Shapes can
then be define based on dynamic points, length, and angles, creating dynamic
shapes.

Of course, at some point we need to resolve all of these dynamic values. We
don't draw a point that has a certain relationship to another point, we draw a
point that has certain coordinates. Getting an numeric values out of
dynamic values is called :term:`resolution` of the dynamic value, and the
resolved numeric values are called :term:`static values <static value>`.
Importantly, resolving a dynamic value doesn't do anything to the value
itself, it simply traces the dynamic relationships all the way down until it
finds a fixed value, and then applies the appropriate string of relationships
to get the resolved static value.

This means that static values are *snapshots* of a dynamic value at a
particular point in time. If you change any of the values that the dynamic
value depends on and then resolve it again, the static value could be
different, which of course is the whole point of using dynamic values.

As Methods and Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~

The general convention is that dynamic values are accessible as *properties*
of objects. For instance, the `~pyps.shapes.Box.lowerleft` property of the
`~pyps.shapes.Box` class provides a `~pyps.geom.Point` object which will
always represent the lower left corner of the box (the minimum X and minimum Y
coordinates), even if the box changes.
To get the static values for this point, you would simply resolve the
`~pyps.geom.Point` object itself, using `get_coords() 
<~pyps.geom.Point.get_coords>`.

Static values, on the other hand, are retrieved
through various ``get_*`` methods on the object, like the
`~pyps.geom.Point.get_coords` method of ``Point`` objects, or the
`~pyps.shapes.Box.get_bounds` method of ``Box`` objects.


.. # vim: set tw=78:

