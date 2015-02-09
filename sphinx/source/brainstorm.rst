
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


Transformations
~~~~~~~~~~~~~~~~

We will also define several different types of transformations for points, from
which other derived points can be generated. For instance, a simple
transformation might be a *translation* of a source point a certain distance
along a vector (represented by two other points).

Creating transforms as wrappers doesn't seem to want to work well. It's
difficult to do in a useful object oriented way (how do you provide correct
access to the useful points and lengths specific to a shape?), and many of
them seem impossible, particularly angles. How do you know the effects of a
transformation on an angle. Is it always prserved for linear transformations?
Maybe it is. So maybe I can do it.


Layers
----------------

Initially, we won't have an explicit "z-layer" attribute for shapes. Instead,
shapes will simply be drawn in the order in which they are added to the
"canvas" (or whatever we call it). But to make this easier, we will define
a pseudo-shape called a Layer (which is really just a Group) to which other
shapes can be added, and then those layers can be added to the canvas in the
correct order to layer the shapes within them.

Factory Functions
--------------------

Whatever class we have to represent a drawing (e.g., ``Canvas``), will have
built in factory methods for every one of the predefined Shape classes, which
not only creates and returns the specified shape, but also adds the shape to
itself. The same goes for all Group type shape classes: they will have factory
functions to create a Shape and add it to themselves.


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


Writers
------------

Despite only being able to support output to postscript initially (see the
TeX_ section), I still want to separate front-end and back-end: the object
stuff, and the thing that actually produces output. Initially, there will only
be one backend, at least to support typesetting, but in theory we could add
more.

The division will be supported because every shape will provide an API that
represents the object as a composition of a few primitives, like lines,
curves, and paths. No matter how complex the shape is, it must be able to
break down this way so that writers do not need to know how to output every
single shape, they only need to know how to do basic primitives.

The method that writers call to get the primitives of a shape will include an
optional version number argument, or else more generally a *capabilities*
argument. This will specify what types of primitives it can support. There
will be a minimum set of primitives that each writer must support, but then we
might add some more sophisticated optional primitives on top of those. The
shape can then: a) issue an error if they need a capability that isn't
supported (e.g., TeX for non-PS output, initially); b) choose a more compact
or better set of primitives to describe itself based on the capabilities.

For the latter, as a silly example, if the base set of primitives was just
straight lines, then a Circle would have to be able to represent itself with a
series of short straight lines. This would be a very large and not very
accurate representation of the circle. But if another writer comes along that
supports primitive circles, then the Circle could represent itself directly
with that primitive: more compact and presumably more accurate.

Groups
-------------

The ``Group`` class will ``Shape``, but we call it a *pseudo-shape*, because
all it actually does is act as a container for other shapes. When it's time to
write, it will simply iterate over all of the shapes it contains and yield out
those shapes' primitives, for instance.

Transforms
----------------

Distinct from the *transformations* described above for points, a transform is
transformation of the coordinate set as is typical in drawing environments:
scale, translate, rotate, or affline matrix transform. We could supply these
for each shape, but I think to keep things simple, initially we will define a
specific pseudo-shape class just for handling them. It will act as a container
and will automatically do the appropriate local-to-global conversions when
returning shapes.

This means that the primitive shapes the writers use might want to be
something rather different than Shapes. Because it won't necessarily always be
a ``Circle`` class, for instance, representing a circle. Or maybe it can. I
guess there's no reason it couldn't.


.. %
   vim: set tw=78:
    
