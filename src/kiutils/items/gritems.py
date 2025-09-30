"""The graphical items are footprint and board items that are outside of the connectivity items.
   This includes graphical items on technical, user, and copper layers. Graphical items are also
   used to define complex pad geometries.

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0

Major changes:
    10.02.2022 - created

Documentation taken from:
    https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphic_items
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List

from kiutils.items.common import Effects, Position, RenderCache, Stroke
from kiutils.utils.string_utils import *
from kiutils.utils.format_utils import format_float
from kiutils.utils.parsing_utils import parse_bool, format_bool_raw
from kiutils.utils.sexpr import sexp_to_string

@dataclass
class GrText():
    """The ``gr_text`` token defines a graphical text.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_text
    """

    text: str = ""
    """The ``text`` attribute is a string that defines the text"""

    knockout: bool = False
    """The ``knockout`` token defines if the text is inverted (means transparent text and colored
    background insted of colored text and transparent background)"""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` defines the X and Y position coordinates and optional orientation angle of 
    the text"""

    layer: Optional[str] = None
    """The ``layer`` token defines the canonical layer the text resides on"""

    effects: Effects = field(default_factory=lambda: Effects())
    """The ``effects`` token defines how the text is displayed"""

    tstamp: Optional[str] = None      # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the text object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    renderCache: Optional[RenderCache] = None
    """If the ``effects`` token prescribe a TrueType font then the optional ``render_cache`` token 
    should be given in case the font can not be found on the current system.
    
    Available since KiCad v7"""

    @classmethod
    def from_sexpr(cls, exp: list) -> GrText:
        """Convert the given S-Expresstion into a GrText object

        Args:
            - exp (list): Part of parsed S-Expression ``(gr_text ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not gr_text

        Returns:
            - GrText: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'gr_text':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.text = exp[1]
        for item in exp[2:]:
            if parse_bool(item, 'locked'): object.locked = True
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'layer':
                object.layer = item[1]
                if (len(item) > 2) and item[2] == "knockout":
                    object.knockout = True
            elif item[0] == 'effects': object.effects = Effects().from_sexpr(item)
            elif item[0] == 'tstamp': object.tstamp = item[1]
            elif item[0] == 'uuid': object.tstamp = item[1] # Haha :)
            elif item[0] == 'render_cache': object.renderCache = RenderCache.from_sexpr(item)
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 2, newline: bool = True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 2.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ['gr_text', escape_and_quote(self.text)]

        expr.append(format_bool_raw('locked', self.locked))

        pos = ['at', format_float(self.position.X), format_float(self.position.Y)]
        if self.position.angle is not None:
            pos.append(format_float(self.position.angle))
        expr.append(pos)

        layer = ['layer', escape_and_quote(self.layer)] if self.layer is not None else None
        if layer and self.knockout:
            layer.append('knockout')
        if layer:
            expr.append(layer)

        if self.tstamp is not None:
            expr.append(['uuid', quote(self.tstamp)])

        expr.append(self.effects._to_sexpr_raw())

        if self.renderCache is not None:
            expr.append(self.renderCache._to_sexpr_raw())

        return expr

@dataclass
class GrTextBox():
    """The ``gr_text_box`` token defines a graphical rectangle containing line-wrapped text.

    Available since KiCad v7
    
    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_text_box
    """

    locked: bool = False
    """The ``locked`` token specifies if the text box can be moved. Defaults to ``False``."""

    text: str = ""
    """The ``text`` token defines the content of the text box. Defaults to an empty string."""

    start: Optional[Position] = None
    """The optional ``start`` token defines the top-left of a cardinally oriented text box"""

    end: Optional[Position] = None
    """The optional ``end`` token defines the bottom-right of a cardinally oriented text box"""

    pts: List[Position] = field(default_factory=list)
    """The ``pts`` token defines the four corners of a non-cardianlly oriented text box. The corners
    must be in order, but the winding can be either direction."""

    angle: Optional[float] = None
    """The optional ``angle`` token defines the rotation of the text box in degrees.

    Note:
        - If ``angle`` is not given, or is a cardinal angle (0, 90, 180 or 270), then the text box
          MUST have ``start`` and ``end`` tokens.
        - If ``angle`` is given and is not a cardinal angle, then the text box MUST have a ``pts``
          token (with 4 pts).
    """

    layer: str = "F.Cu"
    """The ``layer`` token defines the canonical layer the text box resides on. Defaults to
    ``F.Cu``."""

    tstamp: Optional[str] = None
    """The optional ``tstamp`` token defines the unique identifier of the text box"""

    effects: Optional[Effects] = None
    """The optional ``effects`` token describes the style of the text in the text box"""

    stroke: Optional[Stroke] = None
    """The optional ``stroke`` token describes the style of an optional border to be drawn around 
    the text box"""

    renderCache: Optional[RenderCache] = None
    """If the ``effects`` token prescribe a TrueType font then the optional ``render_cache`` token 
    should be given in case the font can not be found on the current system.
    
    Available since KiCad v7"""

    @classmethod
    def from_sexpr(cls, exp: list) -> GrTextBox:
        raise Exception('We never dealt with this before.'
                        'Most definitely there were changes introduced between Kicad 7 and 9.'
                        'If you know what you are doing, proceed to verify/fix and remove the exception,'
                        'or contact the maintainer.')

        # """Convert the given S-Expression into a GrTextBox object
        #
        # Args:
        #     - exp (list): Part of parsed S-Expression ``(gr_text_box ...)``
        #
        # Raises:
        #     - Exception: When given parameter's type is not a list
        #     - Exception: When the first item of the list is not fp_text_box
        #
        # Returns:
        #     - GrTextBox: Object of the class initialized with the given S-Expression
        # """
        # if not isinstance(exp, list) or len(exp) < 2:
        #     raise Exception("Expression does not have the correct type")
        #
        # if exp[0] != 'gr_text_box':
        #     raise Exception("Expression does not have the correct type")
        #
        # object = cls()
        #
        # # Extract "locked" token, if any is present
        # if exp[1] == "locked" and not isinstance(exp[2], list):
        #     object.locked = True
        #     object.text = exp[2]
        #     start_at = 3
        # else:
        #     object.text = exp[1]
        #     start_at = 2
        #
        # for item in exp[start_at:]:
        #     if item[0] == 'start': object.start = Position.from_sexpr(item)
        #     if item[0] == 'end': object.end = Position.from_sexpr(item)
        #     if item[0] == 'pts':
        #         for point in item[1:]:
        #             object.pts.append(Position().from_sexpr(point))
        #     if item[0] == 'angle': object.angle = item[1]
        #     if item[0] == 'layer': object.layer = item[1]
        #     if item[0] == 'tstamp': object.tstamp = item[1]
        #     if item[0] == 'tstamp': object.uuid = item[1] # Haha :)
        #     if item[0] == 'effects': object.effects = Effects.from_sexpr(item)
        #     if item[0] == 'stroke': object.stroke = Stroke.from_sexpr(item)
        #     if item[0] == 'render_cache': object.renderCache = RenderCache.from_sexpr(item)
        #
        # return object

    def to_sexpr(self, indent: int = 2, newline: bool = True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 2.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Raises:
            - Exception: When a non-cardinal angle is given and no corner points were defined using
              the ``self.pts`` token
            - Exception: When a cardinal angle or no angle is given and either start or end token
              is undefined

        Returns:
            - str: S-Expression of this object
        """
        if self.angle is not None and self.angle not in [0.0, 90.0, 180.0, 270.0]:
            if len(self.pts) != 4:
                raise Exception("None-cardinal angles must have exactly four corner points defined")
        if self.angle is None or self.angle in [0.0, 90.0, 180.0, 270.0]:
            if self.start is None or self.end is None:
                raise Exception("No angle or a cardinal angle needs a start and end token defined")

        indents = ' '*indent
        endline = '\n' if newline else ''

        tstamp = f' (tstamp {self.tstamp})' if self.tstamp is not None else ''
        angle = f'(angle {self.angle}) ' if self.angle is not None else ''
        start = f'(start {self.start.X} {self.start.Y}) ' if self.start is not None else ''
        end = f'(end {self.end.X} {self.end.Y}) ' if self.end is not None else ''
        locked = ' locked' if self.locked else ''

        expression = f'{indents}(gr_text_box{locked} "{dequote(self.text)}"\n'
        if len(self.pts) == 4:
            expression += f'{indents}  (pts\n'
            expression += f'{indents}    (xy {self.pts[0].X} {self.pts[0].Y})        (xy {self.pts[1].X} {self.pts[1].Y})        (xy {self.pts[2].X} {self.pts[2].Y})        (xy {self.pts[3].X} {self.pts[3].Y})\n'
            expression += f'{indents}  )\n'
        expression += f'{indents}  {start}{end}{angle}(layer "{dequote(self.layer)}"){tstamp}\n'
        if self.effects is not None:
            expression += self.effects.to_sexpr(indent+2)
        if self.stroke is not None:
            expression += self.stroke.to_sexpr(indent+2)
        if self.renderCache is not None:
            expression += self.renderCache.to_sexpr(indent+2)
        expression += f'{indents}){endline}'
        return expression

@dataclass
class GrLine():
    """The ``gr_line`` token defines a graphical line.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_line
    """

    start: Position = field(default_factory=lambda: Position())
    """The ``start`` token defines the coordinates of the start of the line"""

    end: Position = field(default_factory=lambda: Position())
    """The ``end`` token defines the coordinates of the end of the line"""

    angle: Optional[float] = None
    """The optional ``angle`` token defines the rotational angle of the line"""

    layer: Optional[str] = None
    """The ``layer`` token defines the canonical layer the rectangle resides on"""

    width: Optional[float] = None     # Used for KiCad < 7
    """The ``width`` token defines the line width of the rectangle. (prior to version 7)"""

    stroke: Optional[GrStroke] = None # Alternative to above

    tstamp: Optional[str] = None      # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the rectangle object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    @classmethod
    def from_sexpr(cls, exp: list) -> GrLine:
        """Convert the given S-Expresstion into a GrLine object

        Args:
            - exp (list): Part of parsed S-Expression ``(gr_line ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not gr_line

        Returns:
            - GrLine: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'gr_line':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if parse_bool(item, 'locked'): object.locked = True
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'start': object.start = Position.from_sexpr(item)
            elif item[0] == 'end': object.end = Position.from_sexpr(item)
            elif item[0] == 'layer': object.layer = item[1]
            elif item[0] == 'tstamp': object.tstamp = item[1]
            elif item[0] == 'uuid': object.tstamp = item[1] # Haha :)
            elif item[0] == 'width': object.width = item[1]
            elif item[0] == 'stroke': object.stroke = GrStroke().from_sexpr(item)
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 2, newline: bool = True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 2.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = [
            'gr_line',
            ['start', format_float(self.start.X), format_float(self.start.Y)],
            ['end', format_float(self.end.X), format_float(self.end.Y)],
        ]

        if self.angle is not None: expr.append(['angle', format_float(self.angle)])
        if self.width is not None:
            if self.stroke is not None:
                raise Exception("I didn't expect both stroke and width. Something is off...")
            expr.append(['width', format_float(self.width)])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        expr.append(format_bool_raw('locked', self.locked))

        if self.layer is not None:
            expr.append(['layer', escape_and_quote(self.layer)])

        if self.tstamp is not None:
            expr.append(['uuid', quote(self.tstamp)])

        return expr


@dataclass
class GrRect():
    """The ``gr_rect`` token defines a graphical rectangle.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_rectangle
    """

    start: Position = field(default_factory=lambda: Position())
    """The ``start`` token defines the coordinates of the upper left corner of the rectangle"""

    end: Position = field(default_factory=lambda: Position())
    """The ``end`` token defines the coordinates of the low right corner of the rectangle"""

    layer: Optional[str] = None
    """The ``layer`` token defines the canonical layer the rectangle resides on"""

    width: Optional[float] = None     # Used for KiCad < 7
    """The ``width`` token defines the line width of the rectangle. (prior to version 7)"""

    stroke: Optional[GrStroke] = None # Alternative to above

    fill: Optional[str] = None
    """The optional ``fill`` toke defines how the rectangle is filled. Valid fill types are solid and none. If not defined, the rectangle is not filled"""

    tstamp: Optional[str] = None      # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the rectangle object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    @classmethod
    def from_sexpr(cls, exp: list) -> GrRect:
        """Convert the given S-Expresstion into a GrRect object

        Args:
            - exp (list): Part of parsed S-Expression ``(gr_rect ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not gr_rect

        Returns:
            - GrRect: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'gr_rect':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if parse_bool(item, 'locked'): object.locked = True
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'start': object.start = Position.from_sexpr(item)
            elif item[0] == 'end': object.end = Position.from_sexpr(item)
            elif item[0] == 'layer': object.layer = item[1]
            elif item[0] == 'tstamp': object.tstamp = item[1]
            elif item[0] == 'uuid': object.tstamp = item[1] # Haha :)
            elif item[0] == 'fill': object.fill = item[1]
            elif item[0] == 'width': object.width = item[1]
            elif item[0] == 'stroke': object.stroke = GrStroke().from_sexpr(item)
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 2, newline: bool = True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 2.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = [
            'gr_rect',
            ['start', format_float(self.start.X), format_float(self.start.Y)],
            ['end', format_float(self.end.X), format_float(self.end.Y)],
        ]

        if self.width is not None:
            if self.stroke is not None:
                raise Exception("I didn't expect both stroke and width. Something is off...")
            expr.append(['width', format_float(self.width)])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        if self.fill is not None:
            expr.append(['fill', self.fill])

        expr.append(format_bool_raw('locked', self.locked))

        if self.layer is not None:
            expr.append(['layer', escape_and_quote(self.layer)])

        if self.tstamp is not None:
            expr.append(['uuid', quote(self.tstamp)])

        return expr


@dataclass
class GrCircle():
    """The ``gr_circle `` token defines a graphical circle.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_circle
    """

    center: Position = field(default_factory=lambda: Position())
    """The ``center`` token defines the coordinates of the center of the circle"""

    end: Position = field(default_factory=lambda: Position())
    """The ``end`` token defines the coordinates of the low right corner of the circle"""

    layer: Optional[str] = None
    """The ``layer`` token defines the canonical layer the circle resides on"""

    width: Optional[float] = None     # Used for KiCad < 7
    """The ``width`` token defines the line width of the circle. (prior to version 7)"""

    stroke: Optional[GrStroke] = None # Alternative to above

    fill: Optional[str] = None
    """The optional ``fill`` toke defines how the circle is filled. Valid fill types are solid and none. If not defined, the rectangle is not filled"""

    tstamp: Optional[str] = None      # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the circle object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    @classmethod
    def from_sexpr(cls, exp: list) -> GrCircle:
        """Convert the given S-Expresstion into a GrCircle object

        Args:
            - exp (list): Part of parsed S-Expression ``(gr_circle ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not gr_circle

        Returns:
            - GrCircle: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'gr_circle':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if parse_bool(item, 'locked'): object.locked = True
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'center': object.center = Position.from_sexpr(item)
            elif item[0] == 'end': object.end = Position.from_sexpr(item)
            elif item[0] == 'layer': object.layer = item[1]
            elif item[0] == 'tstamp': object.tstamp = item[1]
            elif item[0] == 'uuid': object.tstamp = item[1] # Haha :)
            elif item[0] == 'fill': object.fill = item[1]
            elif item[0] == 'width': object.width = item[1]
            elif item[0] == 'stroke': object.stroke = GrStroke().from_sexpr(item)
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 2, newline: bool = True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 2.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = [
            'gr_circle',
            ['center', format_float(self.center.X), format_float(self.center.Y)],
            ['end', format_float(self.end.X), format_float(self.end.Y)],
        ]

        if self.width is not None:
            if self.stroke is not None:
                raise Exception("I didn't expect both stroke and width. Something is off...")
            expr.append(['width', format_float(self.width)])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        if self.fill is not None:
            expr.append(['fill', self.fill])

        expr.append(format_bool_raw('locked', self.locked))

        if self.layer is not None:
            expr.append(['layer', escape_and_quote(self.layer)])

        if self.tstamp is not None:
            expr.append(['uuid', quote(self.tstamp)])

        return expr


@dataclass
class GrArc():
    """The ``gr_arc`` token defines a graphic arc.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_arc
    """

    start: Position = field(default_factory=lambda: Position())
    """The ``start`` token defines the coordinates of the start position of the arc radius"""

    mid: Position = field(default_factory=lambda: Position())
    """The ``mid`` token defines the coordinates of the midpoint along the arc"""

    end: Position = field(default_factory=lambda: Position())
    """The ``end`` token defines the coordinates of the end position of the arc radius"""

    layer: Optional[str] = None
    """The ``layer`` token defines the canonical layer the arc resides on"""

    width: Optional[float] = None     # Used for KiCad < 7
    """The ``width`` token defines the line width of the arc. (prior to version 7)"""

    stroke: Optional[GrStroke] = None # Alternative to above

    tstamp: Optional[str] = None      # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the arc object."""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    @classmethod
    def from_sexpr(cls, exp: list) -> GrArc:
        """Convert the given S-Expresstion into a GrArc object

        Args:
            - exp (list): Part of parsed S-Expression ``(gr_arc ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not gr_arc

        Returns:
            - GrArc: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'gr_arc':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if parse_bool(item, 'locked'): object.locked = True
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'start': object.start = Position.from_sexpr(item)
            elif item[0] == 'mid': object.mid = Position.from_sexpr(item)
            elif item[0] == 'end': object.end = Position.from_sexpr(item)
            elif item[0] == 'layer': object.layer = item[1]
            elif item[0] == 'tstamp': object.tstamp = item[1]
            elif item[0] == 'uuid': object.tstamp = item[1] # Haha :)
            elif item[0] == 'width': object.width = item[1]
            elif item[0] == 'stroke': object.stroke = GrStroke().from_sexpr(item)
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 2, newline: bool = True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 2.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = [
            'gr_arc',
            ['start', format_float(self.start.X), format_float(self.start.Y)],
            ['mid', format_float(self.mid.X), format_float(self.mid.Y)],
            ['end', format_float(self.end.X), format_float(self.end.Y)],
        ]

        if self.width is not None:
            if self.stroke is not None:
                raise Exception("I didn't expect both stroke and width. Something is off...")
            expr.append(['width', format_float(self.width)])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        expr.append(format_bool_raw('locked', self.locked))

        if self.layer is not None:
            expr.append(['layer', escape_and_quote(self.layer)])

        if self.tstamp is not None:
            expr.append(['uuid', quote(self.tstamp)])

        return expr


@dataclass
class GrPoly():
    """The ``gr_poly`` token defines a graphic polygon in a footprint definition.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_polygon
    """

    layer: Optional[str] = None
    """The ``coordinates`` define the list of X/Y coordinates of the polygon outline"""

    coordinates: List[Position] = field(default_factory=list)
    """The ``layer`` token defines the canonical layer the polygon resides on"""

    width: Optional[float] = None     # Used for KiCad < 7
    """The ``width`` token defines the line width of the polygon. (prior to version 7)"""

    stroke: Optional[GrStroke] = None # Alternative to above

    fill: Optional[str] = None
    """The optional ``fill`` toke defines how the polygon is filled. Valid fill types are solid and none. If not defined, the rectangle is not filled"""

    tstamp: Optional[str] = None      # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the polygon object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    @classmethod
    def from_sexpr(cls, exp: list) -> GrPoly:
        """Convert the given S-Expresstion into a GrPoly object

        Args:
            - exp (list): Part of parsed S-Expression ``(gr_poly ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not gr_poly

        Returns:
            - GrPoly: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'gr_poly':
            raise Exception("Expression does not have the correct type")

        object = cls()

        for item in exp[1:]:
            if parse_bool(item, 'locked'): object.locked = True
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'pts':
                for point in item[1:]: object.coordinates.append(Position().from_sexpr(point))
            elif item[0] == 'layer': object.layer = item[1]
            elif item[0] == 'tstamp': object.tstamp = item[1]
            elif item[0] == 'uuid': object.tstamp = item[1] # Haha :)
            elif item[0] == 'fill': object.fill = item[1]
            elif item[0] == 'width': object.width = item[1]
            elif item[0] == 'stroke': object.stroke = GrStroke().from_sexpr(item)
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 2, newline: bool = True, pts_newline: bool = False) -> str:
        """Generate the S-Expression representing this object. When no coordinates are set
        in the polygon, the resulting S-Expression will be left empty.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 2.
            - newline (bool): Adds a newline for the ``(pts ..)`` token as KiCad treats
                              this different in Board files than Footprint files. Defaults to
                              False.
            - pts_newline (bool): Adds a newline for the ``(pts ..)`` token. Defaults to False.

        Returns:
            - str: S-Expression of this object
        """
        if len(self.coordinates) == 0:
            return ''

        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ['gr_poly']

        pts = ['pts']
        for point in self.coordinates:
            pts.append(['xy', format_float(point.X), format_float(point.Y)])
        expr.append(pts)

        if self.width is not None:
            if self.stroke is not None:
                raise Exception("I didn't expect both stroke and width. Something is off...")
            expr.append(['width', format_float(self.width)])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        if self.fill is not None:
            expr.append(['fill', self.fill])

        expr.append(format_bool_raw('locked', self.locked))

        if self.layer is not None:
            expr.append(['layer', escape_and_quote(self.layer)])

        if self.tstamp is not None:
            expr.append(['uuid', quote(self.tstamp)])

        return expr


@dataclass
class GrCurve():
    """The ``gr_curve`` token defines a graphic Cubic Bezier curve in a footprint definition.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_curve
    """
    coordinates: List[Position] = field(default_factory=list)
    """The ``coordinates`` define the list of X/Y coordinates of the curve outline"""

    layer: Optional[str] = None
    """The ``layer`` token defines the canonical layer the curve resides on"""

    width: Optional[float] = None     # Used for KiCad < 7
    """The ``width`` token defines the line width of the curve. (prior to version 7)"""

    stroke: Optional[GrStroke] = None # Alternative to above

    tstamp: Optional[str] = None      # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the curve object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    @classmethod
    def from_sexpr(cls, exp: list) -> GrCurve:
        """Convert the given S-Expresstion into a GrCurve object

        Args:
            - exp (list): Part of parsed S-Expression ``(gr_curve ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not gr_curve

        Returns:
            - GrCurve: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'gr_curve':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if parse_bool(item, 'locked'): object.locked = True
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'pts':
                for point in item[1:]: object.coordinates.append(Position().from_sexpr(point))
            elif item[0] == 'layer': object.layer = item[1]
            elif item[0] == 'tstamp': object.tstamp = item[1]
            elif item[0] == 'uuid': object.tstamp = item[1] # Haha :)
            elif item[0] == 'width': object.width = item[1]
            elif item[0] == 'stroke': object.stroke = GrStroke().from_sexpr(item)
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 2, newline: bool = True) -> str:
        """Generate the S-Expression representing this object. When no coordinates are set
        in the curve, the resulting S-Expression will be left empty.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 2.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        if len(self.coordinates) == 0:
            return ''

        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ['gr_curve']

        pts = ['pts']
        for point in self.coordinates:
            pts.append(['xy', format_float(point.X), format_float(point.Y)])
        expr.append(pts)

        if self.width is not None:
            if self.stroke is not None:
                raise Exception("I didn't expect both stroke and width. Something is off...")
            expr.append(['width', format_float(self.width)])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        expr.append(format_bool_raw('locked', self.locked))

        if self.layer is not None:
            expr.append(['layer', escape_and_quote(self.layer)])

        if self.tstamp is not None:
            expr.append(['uuid', quote(self.tstamp)])

        return expr


@dataclass
class GrStroke():

    width: float = 0.0

    type: str = ""

    @classmethod
    def from_sexpr(cls, exp: list) -> GrStroke:
        """Convert the given S-Expresstion into a GrStroke object

        Args:
            - exp (list): Part of parsed S-Expression ``(stroke ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not stroke

        Returns:
            - KeepoutSettings: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'stroke':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'width': object.width = item[1]
            elif item[0] == 'type': object.type = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 0, newline: bool = False) -> str:
        """Generate the S-Expression representing this object.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to False.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        return ['stroke', ['width', format_float(self.width)], ['type', self.type]]
