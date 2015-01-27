#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps.writers import Writer


class EPSWriter(Writer):
    """
    A writer for generated Encapsulated PostScript files.
    """

    def render_primitive(self, primitive):
        command = primitive[0]
        if command == "circle":
            return "%f %f %f 0 360 arc closepath stroke" % primitive[1:]

        raise KeyError('Unknow primitive: %s' % command)
    
    def write(self, ostream, document, verbose=False):
        ostream.write(r"""%!PS-Adobe-3.0 EPSF-3.0
%%BoundingBox 0 0 100 100
%%Creator: pyps
%%Pages: 1

""")

        for shape in document.itershapes():
            if verbose:
                ostream.write("%% Shape: %s\n" % str(shape))
            ostream.write("\n".join(self.render_primitive(p) for p in shape.render()))
            ostream.write("\n\n")

        ostream.write(r"""
%%EOF
""")

