#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

from pyps.writers import Writer

from pyps.shapes import Path


class EPSWriter(Writer):
    """
    A writer for generated Encapsulated PostScript files.
    """

    def __init__(self):
        super(EPSWriter, self).__init__()
        self._tab = '    '
        self._indent = 0
        self._prefix = ''
        self._verbose = False
        self._ostream = None

    def indent(self):
        if self._verbose:
            self._indent += 1
            self._prefix += self._tab

    def outdent(self):
        if self._verbose and self._indent > 0:
            self._indent -= 1
            self._prefix = self._tab * self._indent

    def render_color(self, color):
        return ' '.join(str(c) for c in color.rgbf())

    def render_path(self, path):
        if not isinstance(path, Path):
            raise TypeError('Render returned non-Path: %r' % (path,))


        self.write_line('newpath')
        self.indent()

        for comp in path:
            self._render_path_component(comp)

        fill = path.get_fill()
        stroke = path.get_stroke()

        if fill:
            self.write_line('%s setrgbcolor gsave fill grestore' % (self.render_color(fill)))
        if stroke:
            self.write_line('%s setrgbcolor %f setlinewidth stroke' % (self.render_color(stroke), path.get_stroke_width()))

        self.outdent()

    def _render_path_component(self, comp):
            command = comp[0]
            if command == 'M':
                self.write_seg('%f %f moveto' % comp[1:])
            elif command == 'm':
                self.write_seg('%f %f rmoveto' % comp[1:])
            elif command == 'L':
                self.write_seg('%f %f lineto' % comp[1:])
            elif command == 'l':
                self.write_seg('%f %f rlineto' % comp[1:])
            elif command == 'A':
                cx, cy, r, b, e, ccw = comp[1:]
                op = 'arc' if ccw else 'arcn'
                self.write_seg('%s %s %s %s %s %s' % (cx, cy, r, b, e, op))
            elif command == 'C':
                #Circle
                cx, cy, r = comp[1:]
                self.write_seg('%s %s %s 0 360 arc' % (cx, cy, r))
            elif command == 'X':
                self.write_seg('closepath')
            elif command == 'xfT':
                dx, dy, subpaths = comp[1:]
                self.write_line('gsave %s %s translate' % (dx, dy))
                self.indent()
                for p in subpaths:
                    self.render_path(p)
                self.outdent()
                self.write_line('grestore')
            else:
                raise ValueError('Unknown path component command: %r' % (command,))
                
    def write_seg(self, segment):
        if self._ostream:
            if self._verbose:
                self.write_line(segment)
            else:
                self._ostream.write(' %s ' % (segment,))

    def write_line(self, line=None):
        if self._ostream:
            if line is None:
                self._ostream.write('\n')
            else:
                self._ostream.write('%s%s\n' % (self._prefix, line))

    
    def write(self, ostream, document, verbose=False):
        was_verbose = self._verbose
        self._verbose = verbose
        self._ostream = ostream

        try:
            #FIXME: Set the bounding box correctly.
            ostream.write(r"""%!PS-Adobe-3.0 EPSF-3.0
%%BoundingBox 0 0 100 100
%%Creator: pyps
%%Pages: 1

""")

            for shape in document.itershapes():
                if verbose:
                    self.write_line("%% Shape: %s" % str(shape))

                for p in shape.render():
                    self.render_path(p)
                ostream.write("\n\n")

            ostream.write(r"""
%%EOF
""")
        finally:
            self._verbose = was_verbose
            self._ostream = None

