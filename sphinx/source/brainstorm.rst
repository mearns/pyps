
Developer Brainstorming
=========================

Points
---------------

There are two types of points: :dfn:`specified points` and :dfn:`derived
points`.

A :term:`specified point` is one that the user specifies in constructing,
placing, or otherwise defining a graphical object. Things like the center of a
circle or the vertices of an polyline are specified points.

A :term:`derived point` is one the falls out of the definition of a shape. For
instance, a regular pentagon may be defined by a center point (a *specified
point*) and a vector giving it's apothem, for instance. In this case, the
points corresponding to the five vertices of the pentagon would be *derived
points*.

Specified points can be specified directly and entirely by the user and can be
directly changed for a given shape (e.g., you can move a circle by changing
it's center point). Derived points are not directly manipulated by the user,
they are a consequence of the corresponding specified points, and geometry.

Specified points are just simple tuples and are mutable, and the point objects
specified in shape constructors are always retained within the shape. That
means methods like ``move`` will actually modify the point object, so if the
same object is used as a specified point for another shape, that shape will
change as well.

Of course, you can also use derived points from one shape as specified points
for another, which means trying to modify the point will fail. This is just a
runtime error, bummer for you.

TeX
---------------

I want to be able to use TeX to generate text, because lots of figures are not
useful without good typesetting, especially of math equations.

I should be able to pretty easily use the TeX binary to generate an EPS of a
mathematical expression, for instance, and then embed the EPS into the output
PostScript, which is why initially I'll only be able to generate postscript as
output.

Ideally, I'd like to be able to use a real postscript interpreter to actually
generate the vectors of the TeX generated EPS, and embed those vectors as
objects directly. But I don't know how much would be involved in that, it
might require writing my own PS interpreter which I don't want to do, it might
be easier to generate a TeX interpreter.


.. %
   vim: set tw=78:
    
