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
from kiutils.utils.parsing_utils import *
from kiutils.utils.sexpr import sexp_to_string


@dataclass
class GrText:
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

    tstamp: Optional[str] = None  # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the text object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    renderCache: Optional[RenderCache] = None
    """If the ``effects`` token prescribe a TrueType font then the optional ``render_cache`` token 
    should be given in case the font can not be found on the current system.
    
    Available since KiCad v7"""

    net: Optional[int] = None
    """The optional ``net`` token defines by net ordinal number which net in the net section that
    the graphical item is part of."""

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

        if exp[0] != "gr_text":
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.text = exp[1]
        for item in exp[2:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "at":
                object.position = Position().from_sexpr(item)
            elif item[0] == "layer":
                object.layer = item[1]
                if (len(item) > 2) and item[2] == "knockout":
                    object.knockout = True
            elif item[0] == "effects":
                object.effects = Effects().from_sexpr(item)
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
            elif item[0] == "render_cache":
                object.renderCache = RenderCache.from_sexpr(item)
            elif item[0] == "net":
                object.net = item[1]
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

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
        expr = ["gr_text", escape_and_quote(self.text)]

        expr.append(format_bool("locked", self.locked))

        pos = ["at", self.position.X, self.position.Y]
        if self.position.angle is not None:
            pos.append(self.position.angle)
        expr.append(pos)

        layer = (
            ["layer", escape_and_quote(self.layer)] if self.layer is not None else None
        )
        if layer and self.knockout:
            layer.append("knockout")
        if layer:
            expr.append(layer)

        if self.net is not None:
            expr.append(["net", self.net])

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        expr.append(self.effects._to_sexpr_raw())

        if self.renderCache is not None:
            expr.append(self.renderCache._to_sexpr_raw())

        return expr


@dataclass
class GrTextBox:
    """The ``gr_text_box`` token defines a graphical rectangle containing line-wrapped text.

    Available since KiCad v7

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_text_box
    """

    text: str = ""
    """The ``text`` token defines the content of the text box."""

    locked: bool = False
    """The ``locked`` token specifies if the text box can be moved."""

    start: Optional[Position] = None
    """The optional ``start`` token defines the top-left of a cardinally oriented text box."""

    end: Optional[Position] = None
    """The optional ``end`` token defines the bottom-right of a cardinally oriented text box."""

    pts: List[Position] = field(default_factory=list)
    """The ``pts`` token defines the four corners of a non-cardinally oriented text box."""

    angle: Optional[float] = None
    """The optional ``angle`` token defines the rotation of the text box in degrees."""

    margins: Optional[List[float]] = None
    """The optional ``margins`` token defines left, top, right, bottom margins."""

    layer: Optional[str] = None
    """The ``layer`` token defines the canonical layer the text box resides on."""

    tstamp: Optional[str] = None
    """The optional ``tstamp`` token defines the unique identifier of the text box."""

    effects: Optional[Effects] = None
    """The optional ``effects`` token describes the style of the text in the text box."""

    border: bool = False
    """The ``border`` token defines whether the border is visible."""

    knockout: bool = False
    """The ``knockout`` token defines if the text is inverted."""

    stroke: Optional[Stroke] = None
    """The optional ``stroke`` token describes the style of an optional border."""

    renderCache: Optional[RenderCache] = None
    """If the ``effects`` token prescribe a TrueType font then the optional
    ``render_cache`` token should be given in case the font can not be found
    on the current system.
    """

    @classmethod
    def from_sexpr(cls, exp: list) -> GrTextBox:
        """Convert the given S-Expression into a GrTextBox object

        Args:
            - exp (list): Part of parsed S-Expression ``(gr_text_box ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not gr_text_box

        Returns:
            - GrTextBox: Object initialized with the given S-Expression
        """

        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "gr_text_box":
            raise Exception("Expression does not have the correct type")

        object = cls()

        object.text = exp[1]

        for item in exp[2:]:

            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")

            elif is_bool_key(item, "border"):
                object.border = parse_bool(item, "border")

            elif is_bool_key(item, "knockout"):
                object.knockout = parse_bool(item, "knockout")

            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )

            elif item[0] == "start":
                object.start = Position().from_sexpr(item)

            elif item[0] == "end":
                object.end = Position().from_sexpr(item)

            elif item[0] == "pts":
                for point in item[1:]:
                    object.pts.append(Position().from_sexpr(point))

            elif item[0] == "angle":
                object.angle = item[1]

            elif item[0] == "margins":
                object.margins = [
                    item[1],
                    item[2],
                    item[3],
                    item[4],
                ]

            elif item[0] == "layer":
                object.layer = item[1]

            elif item[0] == "tstamp":
                object.tstamp = item[1]

            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)

            elif item[0] == "effects":
                object.effects = Effects().from_sexpr(item)

            elif item[0] == "stroke":
                object.stroke = Stroke().from_sexpr(item)

            elif item[0] == "render_cache":
                object.renderCache = RenderCache.from_sexpr(item)

            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

        return object

    def to_sexpr(self, indent: int = 2, newline: bool = True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output.
            - newline (bool): Adds a newline to the end of the output.

        Returns:
            - str: S-Expression of this object
        """

        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):

        # Validation
        if self.angle is not None and self.angle not in [0.0, 90.0, 180.0, 270.0]:
            if len(self.pts) != 4:
                raise Exception(
                    "Non-cardinal angles must have exactly four corner points defined"
                )

        if self.angle is None or self.angle in [0.0, 90.0, 180.0, 270.0]:
            if self.start is None or self.end is None:
                raise Exception(
                    "No angle or a cardinal angle needs a start and end token defined"
                )

        expr = ["gr_text_box", escape_and_quote(self.text)]

        expr.append(format_bool("locked", self.locked))

        # Geometry
        if self.start is not None:
            expr.append(["start", self.start.X, self.start.Y])

        if self.end is not None:
            expr.append(["end", self.end.X, self.end.Y])

        if len(self.pts) > 0:
            pts_expr = ["pts"]

            for point in self.pts:
                pts_expr.append(["xy", point.X, point.Y])

            expr.append(pts_expr)

        # Margins
        if self.margins is not None:
            expr.append(
                [
                    "margins",
                    self.margins[0],
                    self.margins[1],
                    self.margins[2],
                    self.margins[3],
                ]
            )

        # Angle
        if self.angle is not None and self.angle != 0:
            expr.append(["angle", self.angle])

        # Layer
        if self.layer is not None:
            expr.append(["layer", escape_and_quote(self.layer)])

        # UUID
        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        # Text effects
        if self.effects is not None:
            expr.append(self.effects._to_sexpr_raw())

        # Border
        expr.append(format_bool("border", self.border))

        # Stroke
        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        # Knockout
        expr.append(format_bool("knockout", self.knockout))

        # Render cache
        if self.renderCache is not None:
            expr.append(self.renderCache._to_sexpr_raw())

        return expr


@dataclass
class GrLine:
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

    width: Optional[float] = None  # Used for KiCad < 7
    """The ``width`` token defines the line width of the rectangle. (prior to version 7)"""

    stroke: Optional[GrStroke] = None  # Alternative to above

    tstamp: Optional[str] = None  # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the rectangle object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    net: Optional[int] = None
    """The optional ``net`` token defines by net ordinal number which net in the net section that
    the graphical item is part of."""

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

        if exp[0] != "gr_line":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "start":
                object.start = Position.from_sexpr(item)
            elif item[0] == "end":
                object.end = Position.from_sexpr(item)
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
            elif item[0] == "width":
                object.width = item[1]
            elif item[0] == "stroke":
                object.stroke = GrStroke().from_sexpr(item)
            elif item[0] == "net":
                object.net = item[1]
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

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
            "gr_line",
            ["start", self.start.X, self.start.Y],
            ["end", self.end.X, self.end.Y],
        ]

        if self.angle is not None:
            expr.append(["angle", self.angle])
        if self.width is not None:
            if self.stroke is not None:
                raise Exception(
                    "I didn't expect both stroke and width. Something is off..."
                )
            expr.append(["width", self.width])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        expr.append(format_bool("locked", self.locked))

        if self.layer is not None:
            expr.append(["layer", escape_and_quote(self.layer)])

        if self.net is not None:
            expr.append(["net", self.net])

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        return expr


@dataclass
class GrRect:
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

    width: Optional[float] = None  # Used for KiCad < 7
    """The ``width`` token defines the line width of the rectangle. (prior to version 7)"""

    stroke: Optional[GrStroke] = None  # Alternative to above

    fill: Optional[str] = None
    """The optional ``fill`` toke defines how the rectangle is filled. Valid fill types are solid and none. If not defined, the rectangle is not filled"""

    tstamp: Optional[str] = None  # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the rectangle object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    net: Optional[int] = None
    """The optional ``net`` token defines by net ordinal number which net in the net section that
    the graphical item is part of."""

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

        if exp[0] != "gr_rect":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "start":
                object.start = Position.from_sexpr(item)
            elif item[0] == "end":
                object.end = Position.from_sexpr(item)
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
            elif item[0] == "fill":
                object.fill = item[1]
            elif item[0] == "width":
                object.width = item[1]
            elif item[0] == "stroke":
                object.stroke = GrStroke().from_sexpr(item)
            elif item[0] == "net":
                object.net = item[1]
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

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
            "gr_rect",
            ["start", self.start.X, self.start.Y],
            ["end", self.end.X, self.end.Y],
        ]

        if self.width is not None:
            if self.stroke is not None:
                raise Exception(
                    "I didn't expect both stroke and width. Something is off..."
                )
            expr.append(["width", self.width])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        if self.fill is not None:
            expr.append(["fill", self.fill])

        expr.append(format_bool("locked", self.locked))

        if self.layer is not None:
            expr.append(["layer", escape_and_quote(self.layer)])

        if self.net is not None:
            expr.append(["net", self.net])

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        return expr


@dataclass
class GrCircle:
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

    width: Optional[float] = None  # Used for KiCad < 7
    """The ``width`` token defines the line width of the circle. (prior to version 7)"""

    stroke: Optional[GrStroke] = None  # Alternative to above

    fill: Optional[str] = None
    """The optional ``fill`` toke defines how the circle is filled. Valid fill types are solid and none. If not defined, the rectangle is not filled"""

    tstamp: Optional[str] = None  # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the circle object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    net: Optional[int] = None
    """The optional ``net`` token defines by net ordinal number which net in the net section that
    the graphical item is part of."""

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

        if exp[0] != "gr_circle":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "center":
                object.center = Position.from_sexpr(item)
            elif item[0] == "end":
                object.end = Position.from_sexpr(item)
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
            elif item[0] == "fill":
                object.fill = item[1]
            elif item[0] == "width":
                object.width = item[1]
            elif item[0] == "stroke":
                object.stroke = GrStroke().from_sexpr(item)
            elif item[0] == "net":
                object.net = item[1]
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

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
            "gr_circle",
            ["center", self.center.X, self.center.Y],
            ["end", self.end.X, self.end.Y],
        ]

        if self.width is not None:
            if self.stroke is not None:
                raise Exception(
                    "I didn't expect both stroke and width. Something is off..."
                )
            expr.append(["width", self.width])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        if self.fill is not None:
            expr.append(["fill", self.fill])

        expr.append(format_bool("locked", self.locked))

        if self.layer is not None:
            expr.append(["layer", escape_and_quote(self.layer)])

        if self.net is not None:
            expr.append(["net", self.net])

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        return expr


@dataclass
class GrArc:
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

    width: Optional[float] = None  # Used for KiCad < 7
    """The ``width`` token defines the line width of the arc. (prior to version 7)"""

    stroke: Optional[GrStroke] = None  # Alternative to above

    tstamp: Optional[str] = None  # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the arc object."""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    net: Optional[int] = None
    """The optional ``net`` token defines by net ordinal number which net in the net section that
    the graphical item is part of."""

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

        if exp[0] != "gr_arc":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "start":
                object.start = Position.from_sexpr(item)
            elif item[0] == "mid":
                object.mid = Position.from_sexpr(item)
            elif item[0] == "end":
                object.end = Position.from_sexpr(item)
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
            elif item[0] == "width":
                object.width = item[1]
            elif item[0] == "stroke":
                object.stroke = GrStroke().from_sexpr(item)
            elif item[0] == "net":
                object.net = item[1]
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

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
            "gr_arc",
            ["start", self.start.X, self.start.Y],
            ["mid", self.mid.X, self.mid.Y],
            ["end", self.end.X, self.end.Y],
        ]

        if self.width is not None:
            if self.stroke is not None:
                raise Exception(
                    "I didn't expect both stroke and width. Something is off..."
                )
            expr.append(["width", self.width])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        expr.append(format_bool("locked", self.locked))

        if self.layer is not None:
            expr.append(["layer", escape_and_quote(self.layer)])

        if self.net is not None:
            expr.append(["net", self.net])

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        return expr


@dataclass
class GrPoly:
    """The ``gr_poly`` token defines a graphic polygon in a footprint definition.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_polygon
    """

    layer: Optional[str] = None
    """The ``coordinates`` define the list of X/Y coordinates of the polygon outline"""

    coordinates: List[Position] = field(default_factory=list)
    """The ``layer`` token defines the canonical layer the polygon resides on"""

    width: Optional[float] = None  # Used for KiCad < 7
    """The ``width`` token defines the line width of the polygon. (prior to version 7)"""

    stroke: Optional[GrStroke] = None  # Alternative to above

    fill: Optional[str] = None
    """The optional ``fill`` toke defines how the polygon is filled. Valid fill types are solid and none. If not defined, the rectangle is not filled"""

    tstamp: Optional[str] = None  # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the polygon object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    net: Optional[int] = None
    """The optional ``net`` token defines by net ordinal number which net in the net section that
    the graphical item is part of."""

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

        if exp[0] != "gr_poly":
            raise Exception("Expression does not have the correct type")

        object = cls()

        for item in exp[1:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "pts":
                for point in item[1:]:
                    object.coordinates.append(Position().from_sexpr(point))
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
            elif item[0] == "fill":
                object.fill = item[1]
            elif item[0] == "width":
                object.width = item[1]
            elif item[0] == "stroke":
                object.stroke = GrStroke().from_sexpr(item)
            elif item[0] == "net":
                object.net = item[1]
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

        return object

    def to_sexpr(
        self, indent: int = 2, newline: bool = True, pts_newline: bool = False
    ) -> str:
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
            return ""

        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ["gr_poly"]

        pts = ["pts"]
        for point in self.coordinates:
            pts.append(["xy", point.X, point.Y])
        expr.append(pts)

        if self.width is not None:
            if self.stroke is not None:
                raise Exception(
                    "I didn't expect both stroke and width. Something is off..."
                )
            expr.append(["width", self.width])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        if self.fill is not None:
            expr.append(["fill", self.fill])

        expr.append(format_bool("locked", self.locked))

        if self.layer is not None:
            expr.append(["layer", escape_and_quote(self.layer)])

        if self.net is not None:
            expr.append(["net", self.net])

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        return expr


@dataclass
class GrCurve:
    """The ``gr_curve`` token defines a graphic Cubic Bezier curve in a footprint definition.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_curve
    """

    coordinates: List[Position] = field(default_factory=list)
    """The ``coordinates`` define the list of X/Y coordinates of the curve outline"""

    layer: Optional[str] = None
    """The ``layer`` token defines the canonical layer the curve resides on"""

    width: Optional[float] = None  # Used for KiCad < 7
    """The ``width`` token defines the line width of the curve. (prior to version 7)"""

    stroke: Optional[GrStroke] = None  # Alternative to above

    tstamp: Optional[str] = None  # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the curve object"""

    locked: bool = False
    """The ``locked`` token defines if the object may be moved or not"""

    net: Optional[int] = None
    """The optional ``net`` token defines by net ordinal number which net in the net section that
    the graphical item is part of."""

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

        if exp[0] != "gr_curve":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "pts":
                for point in item[1:]:
                    object.coordinates.append(Position().from_sexpr(point))
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
            elif item[0] == "width":
                object.width = item[1]
            elif item[0] == "stroke":
                object.stroke = GrStroke().from_sexpr(item)
            elif item[0] == "net":
                object.net = item[1]
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

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
            return ""

        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ["gr_curve"]

        pts = ["pts"]
        for point in self.coordinates:
            pts.append(["xy", point.X, point.Y])
        expr.append(pts)

        if self.width is not None:
            if self.stroke is not None:
                raise Exception(
                    "I didn't expect both stroke and width. Something is off..."
                )
            expr.append(["width", self.width])

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        expr.append(format_bool("locked", self.locked))

        if self.layer is not None:
            expr.append(["layer", escape_and_quote(self.layer)])

        if self.net is not None:
            expr.append(["net", self.net])

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        return expr


@dataclass
class GrStroke:
    """The ``stroke`` token defines a line-style used to draw the shape's border."""

    width: float = 0.0
    """The ``width`` token defines the line width of a stroke."""

    type: str = ""
    """The ``type`` token defines the type of the stroke (solid, dashed, etc.)."""

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

        if exp[0] != "stroke":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "width":
                object.width = item[1]
            elif item[0] == "type":
                object.type = item[1]
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

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
        return ["stroke", ["width", self.width], ["type", self.type]]


@dataclass
class TableBorder:
    """The ``border`` token defines the outer and header border settings of a ``table``.

    Available since KiCad v9
    """

    external: bool = False
    """The ``external`` token defines if the outer border of the table is drawn."""

    header: bool = False
    """The ``header`` token defines if the border below the header row is drawn."""

    stroke: Optional[Stroke] = None
    """The optional ``stroke`` token describes how the borders are drawn."""

    @classmethod
    def from_sexpr(cls, exp: list) -> TableBorder:
        """Convert the given S-Expression into a TableBorder object

        Args:
            - exp (list): Part of parsed S-Expression ``(border ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not border

        Returns:
            - TableBorder: Object initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "border":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "external"):
                object.external = parse_bool(item, "external")
            elif is_bool_key(item, "header"):
                object.header = parse_bool(item, "header")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "stroke":
                object.stroke = Stroke().from_sexpr(item)
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

        return object

    def to_sexpr(self, indent: int = 0, newline: bool = False) -> str:
        """Generate the S-Expression representing this object"""
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = [
            "border",
            format_bool("external", self.external, yesno=True),
            format_bool("header", self.header, yesno=True),
        ]
        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())
        return expr


@dataclass
class TableSeparators:
    """The ``separators`` token defines the inner separator lines of a ``table``.

    Available since KiCad v9
    """

    rows: bool = False
    """The ``rows`` token defines if separators between rows are drawn."""

    cols: bool = False
    """The ``cols`` token defines if separators between columns are drawn."""

    stroke: Optional[Stroke] = None
    """The optional ``stroke`` token describes how the separators are drawn."""

    @classmethod
    def from_sexpr(cls, exp: list) -> TableSeparators:
        """Convert the given S-Expression into a TableSeparators object

        Args:
            - exp (list): Part of parsed S-Expression ``(separators ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not separators

        Returns:
            - TableSeparators: Object initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "separators":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "rows"):
                object.rows = parse_bool(item, "rows")
            elif is_bool_key(item, "cols"):
                object.cols = parse_bool(item, "cols")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "stroke":
                object.stroke = Stroke().from_sexpr(item)
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

        return object

    def to_sexpr(self, indent: int = 0, newline: bool = False) -> str:
        """Generate the S-Expression representing this object"""
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = [
            "separators",
            format_bool("rows", self.rows, yesno=True),
            format_bool("cols", self.cols, yesno=True),
        ]
        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())
        return expr


@dataclass
class TableCell:
    """The ``table_cell`` token defines a single cell of a ``table``. It behaves like a
    ``gr_text_box`` with additional ``span`` information.

    Available since KiCad v9
    """

    text: str = ""
    """The ``text`` token defines the content of the cell."""

    locked: bool = False
    """The ``locked`` token specifies if the cell can be moved."""

    start: Optional[Position] = None
    """The optional ``start`` token defines the top-left of a cardinally oriented cell."""

    end: Optional[Position] = None
    """The optional ``end`` token defines the bottom-right of a cardinally oriented cell."""

    pts: List[Position] = field(default_factory=list)
    """The ``pts`` token defines the four corners of a non-cardinally oriented cell."""

    margins: Optional[List[float]] = None
    """The optional ``margins`` token defines left, top, right, bottom margins."""

    span: Optional[List[int]] = None
    """The optional ``span`` token defines how many columns and rows the cell spans."""

    angle: Optional[float] = None
    """The optional ``angle`` token defines the rotation of the cell in degrees."""

    layer: Optional[str] = None
    """The ``layer`` token defines the canonical layer the cell resides on."""

    tstamp: Optional[str] = None
    """The optional ``tstamp`` token defines the unique identifier of the cell."""

    effects: Optional[Effects] = None
    """The optional ``effects`` token describes the style of the text in the cell."""

    renderCache: Optional[RenderCache] = None
    """If the ``effects`` token prescribe a TrueType font then the optional
    ``render_cache`` token should be given in case the font can not be found
    on the current system.
    """

    knockout: bool = False
    """The ``knockout`` token defines if the text is inverted."""

    @classmethod
    def from_sexpr(cls, exp: list) -> TableCell:
        """Convert the given S-Expression into a TableCell object

        Args:
            - exp (list): Part of parsed S-Expression ``(table_cell ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not table_cell

        Returns:
            - TableCell: Object initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "table_cell":
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.text = exp[1]

        for item in exp[2:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif is_bool_key(item, "knockout"):
                object.knockout = parse_bool(item, "knockout")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "start":
                object.start = Position().from_sexpr(item)
            elif item[0] == "end":
                object.end = Position().from_sexpr(item)
            elif item[0] == "pts":
                for point in item[1:]:
                    object.pts.append(Position().from_sexpr(point))
            elif item[0] == "margins":
                object.margins = [item[1], item[2], item[3], item[4]]
            elif item[0] == "span":
                object.span = [int(item[1]), int(item[2])]
            elif item[0] == "angle":
                object.angle = item[1]
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]
            elif item[0] == "effects":
                object.effects = Effects().from_sexpr(item)
            elif item[0] == "render_cache":
                object.renderCache = RenderCache.from_sexpr(item)
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

        return object

    def to_sexpr(self, indent: int = 4, newline: bool = True) -> str:
        """Generate the S-Expression representing this object"""
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ["table_cell", escape_and_quote(self.text)]

        if self.locked:
            expr.append(["locked", "yes"])

        if self.start is not None:
            expr.append(["start", self.start.X, self.start.Y])

        if self.end is not None:
            expr.append(["end", self.end.X, self.end.Y])

        if len(self.pts) > 0:
            pts_expr = ["pts"]
            for point in self.pts:
                pts_expr.append(["xy", point.X, point.Y])
            expr.append(pts_expr)

        if self.margins is not None:
            expr.append(
                [
                    "margins",
                    self.margins[0],
                    self.margins[1],
                    self.margins[2],
                    self.margins[3],
                ]
            )

        if self.span is not None:
            expr.append(["span", self.span[0], self.span[1]])

        if self.angle is not None and self.angle != 0:
            expr.append(["angle", self.angle])

        if self.layer is not None:
            expr.append(["layer", escape_and_quote(self.layer)])

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        if self.effects is not None:
            expr.append(self.effects._to_sexpr_raw())

        if self.renderCache is not None:
            expr.append(self.renderCache._to_sexpr_raw())

        if self.knockout:
            expr.append(["knockout", "yes"])

        return expr


@dataclass
class Table:
    """The ``table`` token defines a graphical table on the board.

    Available since KiCad v9

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html
    """

    columnCount: int = 0
    """The ``column_count`` token defines the number of columns in the table."""

    locked: bool = False
    """The ``locked`` token specifies if the table can be moved."""

    layer: Optional[str] = None
    """The ``layer`` token defines the canonical layer the table resides on."""

    border: Optional[TableBorder] = None
    """The optional ``border`` token defines the outer/header border settings."""

    separators: Optional[TableSeparators] = None
    """The optional ``separators`` token defines the inner separator settings."""

    columnWidths: List[float] = field(default_factory=list)
    """The ``column_widths`` token defines the width of each column."""

    rowHeights: List[float] = field(default_factory=list)
    """The ``row_heights`` token defines the height of each row."""

    cells: List[TableCell] = field(default_factory=list)
    """The ``cells`` token defines the list of cells contained in the table."""

    tstamp: Optional[str] = None
    """The optional ``tstamp`` token defines the unique identifier of the table."""

    @classmethod
    def from_sexpr(cls, exp: list) -> Table:
        """Convert the given S-Expression into a Table object

        Args:
            - exp (list): Part of parsed S-Expression ``(table ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not table

        Returns:
            - Table: Object initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "table":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "column_count":
                object.columnCount = int(item[1])
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]
            elif item[0] == "border":
                object.border = TableBorder.from_sexpr(item)
            elif item[0] == "separators":
                object.separators = TableSeparators.from_sexpr(item)
            elif item[0] == "column_widths":
                object.columnWidths = [float(x) for x in item[1:]]
            elif item[0] == "row_heights":
                object.rowHeights = [float(x) for x in item[1:]]
            elif item[0] == "cells":
                for cell in item[1:]:
                    object.cells.append(TableCell.from_sexpr(cell))
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

        return object

    def to_sexpr(self, indent: int = 1, newline: bool = True) -> str:
        """Generate the S-Expression representing this object"""
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ["table", ["column_count", self.columnCount]]

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        if self.locked:
            expr.append(["locked", "yes"])

        if self.layer is not None:
            expr.append(["layer", escape_and_quote(self.layer)])

        if self.border is not None:
            expr.append(self.border._to_sexpr_raw())

        if self.separators is not None:
            expr.append(self.separators._to_sexpr_raw())

        expr.append(["column_widths"] + list(self.columnWidths))
        expr.append(["row_heights"] + list(self.rowHeights))

        cells_expr = ["cells"] + [cell._to_sexpr_raw() for cell in self.cells]
        expr.append(cells_expr)

        return expr
