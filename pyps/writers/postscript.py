#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps.writers import Writer

from pyps.shapes import Path


class EPSWriter(Writer):
    """
    A writer for generated Encapsulated PostScript files.
    """

    def render_color(self, color):
        return ' '.join(str(float(c)/255.0) for c in color)

    def render_path(self, path):
        if not isinstance(path, Path):
            raise TypeError('Render returned non-Path: %r' % (path,))

        ps = ''
        ps += '\n '.join(self._render_path_component(comp) for comp in path)

        fill = path.fill
        stroke = path.stroke

        if fill:
            ps += '\n %s setrgbcolor gsave fill grestore' % (self.render_color(fill))
        if stroke:
            ps += '\n %s setrgbcolor stroke' % (self.render_color(stroke))

        return ps

    def _render_path_component(self, comp):
            command = comp[0]
            if command == 'M':
                return '%f %f moveto' % comp[1:]
            elif command == 'm':
                return '%f %f rmoveto' % comp[1:]
            elif command == 'L':
                return '%f %f lineto' % comp[1:]
            elif command == 'l':
                return '%f %f rlineto' % comp[1:]
            elif command == 'a':
                cx, cy, r, b, e, ccw = comp[1:]
                op = 'arc' if ccw else 'arcn'
                return '%s %s %s %s %s %s' % (cx, cy, r, b, e, op)
            else:
                raise ValueError('Unknown path component command: %r' % (command,))
                

    
    def write(self, ostream, document, verbose=False):
        ostream.write(r"""%!PS-Adobe-3.0 EPSF-3.0
%%BoundingBox 0 0 100 100
%%Creator: pyps
%%Pages: 1

""")

        for shape in document.itershapes():
            if verbose:
                ostream.write("%% Shape: %s\n" % str(shape))
            ostream.write("\n".join(('newpath %s' % self.render_path(p)) for p in shape.render()))
            ostream.write("\n\n")

        ostream.write(r"""
%%EOF
""")

