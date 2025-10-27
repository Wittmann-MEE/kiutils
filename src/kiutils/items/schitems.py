"""Defines items used in KiCad schematic files

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0

Major changes:
    19.02.2022 - created

Documentation taken from:
    https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict

from kiutils.items.common import Fill, Position, ColorRGBA, ProjectInstance, Stroke, Effects, Property
from kiutils.utils.string_utils import *
from kiutils.utils.format_utils import format_float
from kiutils.utils.parsing_utils import *
from kiutils.utils.sexpr import sexp_to_string

@dataclass
class Junction():
    """The ``junction`` token defines a junction in the schematic

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_junction_section
    """

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` defines the X and Y coordinates of the junction"""

    diameter: float = 0
    """The ``diameter`` token attribute defines the DIAMETER of the junction. A diameter of 0
       is the default diameter in the system settings."""

    color: ColorRGBA = field(default_factory=lambda: ColorRGBA())
    """The ``color`` token attributes define the Red, Green, Blue, and Alpha transparency of
       the junction. If all four attributes are 0, the default junction color is used."""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Junction:
        """Convert the given S-Expresstion into a Junction object

        Args:
            - exp (list): Part of parsed S-Expression ``(junction ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not junction

        Returns:
            - Junction: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'junction':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'color': object.color = ColorRGBA().from_sexpr(item)
            elif item[0] == 'diameter': object.diameter = item[1]
            elif item[0] == 'uuid': object.uuid = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['junction']

        expr.append(['at', format_float(self.position.X), format_float(self.position.Y)])
        expr.append(['diameter', format_float(self.diameter)])
        expr.append(self.color._to_sexpr_raw())
        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        return expr


@dataclass
class NoConnect():
    """The ``no_connect`` token defines a unused pin connection in the schematic

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_no_connect_section
    """

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` defines the X and Y coordinates of the no connect"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    @classmethod
    def from_sexpr(cls, exp: list) -> NoConnect:
        """Convert the given S-Expresstion into a NoConnect object

        Args:
            - exp (list): Part of parsed S-Expression ``(no_connect ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not no_connect

        Returns:
            - NoConnect: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'no_connect':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['no_connect']

        expr.append(['at', format_float(self.position.X), format_float(self.position.Y)])
        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        return expr


@dataclass
class BusEntry():
    """The ``bus_entry`` token defines a bus entry in the schematic

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_bus_entry_section
    """

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` defines the X and Y coordinates of the bus entry"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    size: Position = field(default_factory=lambda: Position())         # Re-using Position class here
    """The ``size`` token attributes define the X and Y distance of the end point from
       the position of the bus entry"""

    stroke: Stroke = field(default_factory=lambda: Stroke())
    """The ``stroke`` defines how the bus entry is drawn"""

    @classmethod
    def from_sexpr(cls, exp: list) -> BusEntry:
        """Convert the given S-Expresstion into a BusEntry object

        Args:
            - exp (list): Part of parsed S-Expression ``(bus_entry ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not bus_entry

        Returns:
            - BusEntry: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'bus_entry':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'stroke': object.stroke = Stroke().from_sexpr(item)
            elif item[0] == 'size': object.size = Position().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")
        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['bus_entry']

        expr.append(['at', format_float(self.position.X), format_float(self.position.Y)])
        expr.append(['size', format_float(self.size.X), format_float(self.size.Y)])
        expr.append(self.stroke._to_sexpr_raw())
        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        return expr


@dataclass
class BusAlias():
    """The ``bus_alias`` token defines a bus entry in the schematic

    Documentation:
        https://gitlab.com/kicad/services/kicad-dev-docs/-/merge_requests/53/diffs
    """

    name: str = ""
    """The ``name`` of the bus."""

    members: List[str] = field(default_factory=list)
    """The list of ``members`` defined in the bus. Note that when you tap out a bus entry
    from a bus using one these members a label will be created with the selected member name"""

    @classmethod
    def from_sexpr(cls, exp: list) -> BusAlias:
        """Convert the given S-Expresstion into a BusAlias object

        Args:
            - exp (list): Part of parsed S-Expression ``(bus_alias ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not bus_alias
            - Exception: When the S-Expression is not exactly three items long
            - Exception: When the ``members`` token is missing

        Returns:
            - BusAlias: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'bus_alias':
            raise Exception("Expression does not have the correct type")

        if len(exp) != 3:
            raise Exception("Exactly three items are expected in a bus_alias S-Expression.")
        
        if not isinstance(exp[2], list) or exp[2][0] != 'members':
            raise Exception("bus_alias needs to contain a list of members")
        
        object = cls()
        object.name = exp[1]
        object.members = [x for x in exp[2][1:]]
        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        members_quoted = [escape_and_quote(member) for member in self.members]
        return ['bus_alias', escape_and_quote(self.name), ['members'] + members_quoted]


@dataclass
class Connection():
    """The ``wire`` and ``bus`` tokens define wires and buses in the schematic

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_wire_and_bus_section
    """

    type: str = "wire"
    """The ``type`` token defines wether the connection is a ``bus`` or a ``wire``"""

    points: List[Position] = field(default_factory=list)
    """The ``points`` token defines the list of X and Y coordinates of start and end points
       of the wire or bus"""

    stroke: Stroke = field(default_factory=lambda: Stroke())
    """The ``stroke`` defines how the connection is drawn"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Connection:
        """Convert the given S-Expresstion into a Connection object

        Args:
            - exp (list): Part of parsed S-Expression ``(wire ...)`` or ``(bus ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not wire or bus

        Returns:
            - Connection: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if not (exp[0] == 'wire' or exp[0] == 'bus'):
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.type = exp[0]
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'pts':
                for point in item[1:]: object.points.append(Position().from_sexpr(point))
            elif item[0] == 'stroke': object.stroke = Stroke().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = [self.type]

        pts_expr = ['pts']
        for point in self.points:
            pts_expr.append(['xy', format_float(point.X), format_float(point.Y)])
        expr.append(pts_expr)

        expr.append(self.stroke._to_sexpr_raw())

        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        return expr


@dataclass
class PolyLine():
    """The ``polyline`` token defines one or more lines that may or may not represent a polygon

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_graphical_line_section
    """

    points: List[Position] = field(default_factory=list)
    """The ``points`` token defines the list of X/Y coordinates of to draw line(s)
       between. A minimum of two points is required."""

    stroke: Stroke = field(default_factory=lambda: Stroke())
    """The ``stroke`` defines how the graphical line is drawn"""

    fill: Optional[Fill] = None
    """The optional ``fill`` token defines how the graphical line should be filled"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    @classmethod
    def from_sexpr(cls, exp: list) -> PolyLine:
        """Convert the given S-Expresstion into a PolyLine object

        Args:
            - exp (list): Part of parsed S-Expression ``(polyline ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not polyline

        Returns:
            - PolyLine: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'polyline':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'pts':
                for point in item[1:]: object.points.append(Position().from_sexpr(point))
            elif item[0] == 'stroke': object.stroke = Stroke().from_sexpr(item)
            elif item[0] == 'fill': object.fill = Fill().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['polyline']

        pts_expr = ['pts']
        for point in self.points:
            pts_expr.append(['xy', format_float(point.X), format_float(point.Y)])
        expr.append(pts_expr)

        expr.append(self.stroke._to_sexpr_raw())

        if self.fill is not None:
            expr.append(self.fill._to_sexpr_raw())

        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        return expr


@dataclass
class Text():
    """The ``text`` token defines graphical text in a schematic

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_graphical_text_section
    """

    text: str = ""
    """The ``text`` token defines the text string"""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` token defines the X and Y coordinates and rotation angle of the text"""

    effects: Effects = field(default_factory=lambda: Effects())
    """The ``effects`` token defines how the text is drawn"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    # Available since KiCad v9
    # TODO Update docs

    exclude_from_sim: Optional[str] = None

    @classmethod
    def from_sexpr(cls, exp: list) -> Text:
        """Convert the given S-Expresstion into a Text object

        Args:
            - exp (list): Part of parsed S-Expression ``(text ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not text

        Returns:
            - Text: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'text':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.text = exp[1]
        for item in exp[2:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'effects': object.effects = Effects().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
            elif item[0] == 'exclude_from_sim': object.exclude_from_sim = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['text', escape_and_quote(self.text)]

        if self.exclude_from_sim is not None:
            expr.append(['exclude_from_sim', self.exclude_from_sim])

        pos = ['at', format_float(self.position.X), format_float(self.position.Y)]
        if self.position.angle is not None:
            pos.append(format_float(self.position.angle))
        expr.append(pos)

        expr.append(self.effects._to_sexpr_raw())

        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        return expr

@dataclass
class TextBox():
    """The ``text_box`` token defines a text box inside a schematic

    Available since KiCad v7

    Documentation:
        ????
    """
    text: str = ""
    """The ``text`` token defines the text string"""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` token defines the X and Y coordinates and rotation angle of the text"""

    size: Position = field(default_factory=lambda: Position())
    """The ``size`` token defines the size in X and Y direction. Angle is not used."""

    stroke: Stroke = field(default_factory=lambda: Stroke())
    """The ``stroke`` token defines the look of the outline of the text box"""

    fill: Fill = field(default_factory=lambda: Fill())
    """The ``fill`` token defines how the text box should be filled"""

    effects: Effects = field(default_factory=lambda: Effects())
    """The ``effects`` token defines how the text is drawn"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    # Available since KiCad v9

    exclude_from_sim: Optional[str] = None

    margins: List[float] = field(default_factory=list)
    """The ``margins`` token defines the margins of the text box"""

    span: List[int] = field(default_factory=list)
    """The ``span`` token defines the column and row span of the text box"""

    @classmethod
    def from_sexpr(cls, exp: list, table_cell = False) -> TextBox:
        """Convert the given S-Expresstion into a TextBox object

        Args:
            - exp (list): Part of parsed S-Expression ``(text_box ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not text_box

        Returns:
            - TextBox: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        target_type = 'table_cell' if table_cell else 'text_box'
        if exp[0] != target_type:
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.text = exp[1]
        for item in exp[2:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'size': object.size = Position().from_sexpr(item)
            elif item[0] == 'effects': object.effects = Effects().from_sexpr(item)
            elif item[0] == 'stroke': object.stroke = Stroke().from_sexpr(item)
            elif item[0] == 'fill': object.fill = Fill().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
            elif item[0] == 'exclude_from_sim': object.exclude_from_sim = item[1]
            elif item[0] == 'margins': object.margins = [float(margin) for margin in item[1:]]
            elif item[0] == 'span': object.span = (int(item[1]), int(item[2]))
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True, table_cell=False) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 2.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw(table_cell)
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self, table_cell=False):
        target_type = 'table_cell' if table_cell else 'text_box'
        expr = [target_type, escape_and_quote(self.text)]

        if self.exclude_from_sim is not None:
            expr.append(['exclude_from_sim', self.exclude_from_sim])

        pos = ['at', format_float(self.position.X), format_float(self.position.Y)]
        if self.position.angle is not None:
            pos.append(format_float(self.position.angle))
        expr.append(pos)

        expr.append(['size', format_float(self.size.X), format_float(self.size.Y)])
        expr.append(['margins'] + list(map(str, self.margins)))
        if len(self.span) > 0:
            expr.append(['span', self.span[0], self.span[1]])

        expr.append(self.stroke._to_sexpr_raw())
        expr.append(self.fill._to_sexpr_raw())
        expr.append(self.effects._to_sexpr_raw())
        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        return expr


@dataclass
class LocalLabel():
    """The ``label`` token defines an wire or bus label name in a schematic

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#local_label_section
    """

    text: str = ""
    """The ``text`` token defines the text in the label"""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` token defines the X and Y coordinates and rotation angle of the label"""

    effects: Effects = field(default_factory=lambda: Effects())
    """The ``effects`` token defines how the label is drawn"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    fieldsAutoplaced: bool = False
    """The ``fields_autoplaced`` is a flag that indicates that any PROPERTIES associated
    with the global label have been place automatically"""

    properties: list[Property] = field(default_factory=list)

    @classmethod
    def from_sexpr(cls, exp: list) -> LocalLabel:
        """Convert the given S-Expresstion into a LocalLabel object

        Args:
            - exp (list): Part of parsed S-Expression ``(label ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not label

        Returns:
            - LocalLabel: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'label':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.text = exp[1]
        for item in exp[2:]:
            if is_bool_key(item, 'fields_autoplaced'): object.fieldsAutoplaced = parse_bool(item, 'fields_autoplaced')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'effects': object.effects = Effects().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
            elif item[0] == 'property': object.properties.append(Property().from_sexpr(item))
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Exp: {exp}")
            
        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['label', escape_and_quote(self.text)]

        pos = ['at', format_float(self.position.X), format_float(self.position.Y)]
        if self.position.angle is not None:
            pos.append(format_float(self.position.angle))
        expr.append(pos)

        expr.append(format_bool('fields_autoplaced', self.fieldsAutoplaced))
        expr.append(self.effects._to_sexpr_raw())
        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        for prop in self.properties:
            expr.append(prop._to_sexpr_raw())

        return expr


@dataclass
class GlobalLabel():
    """The ``global_label`` token defines a label name that is visible across all schematics in a design

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_global_label_section
    """

    text: str = ""
    """The ``text`` token defines the text in the label"""

    shape: str = "input"
    """The ``shape`` token defines the way the global label is drawn. Possible values are:
       ``input``, ``output``, ``bidirectional``, ``tri_state``, ``passive``."""

    fieldsAutoplaced: bool = False
    """The ``fields_autoplaced`` is a flag that indicates that any PROPERTIES associated
       with the global label have been place automatically"""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` token defines the X and Y coordinates and rotation angle of the label"""

    effects: Effects = field(default_factory=lambda: Effects())
    """The ``effects`` token defines how the label is drawn"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    properties: List[Property] = field(default_factory=list)
    """	The ``properties`` token defines a list of properties of the global label. Currently, the
    only supported property is the inter-sheet reference"""

    @classmethod
    def from_sexpr(cls, exp: list) -> GlobalLabel:
        """Convert the given S-Expresstion into a GlobalLabel object

        Args:
            - exp (list): Part of parsed S-Expression ``(global_label ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not global_label

        Returns:
            - GlobalLabel: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'global_label':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.text = exp[1]
        for item in exp[2:]:
            if is_bool_key(item, 'fields_autoplaced'): object.fieldsAutoplaced = parse_bool(item, 'fields_autoplaced')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'effects': object.effects = Effects().from_sexpr(item)
            elif item[0] == 'property': object.properties.append(Property().from_sexpr(item))
            elif item[0] == 'shape': object.shape = item[1]
            elif item[0] == 'uuid': object.uuid = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['global_label', escape_and_quote(self.text)]

        expr.append(['shape', self.shape])

        pos = ['at', format_float(self.position.X), format_float(self.position.Y)]
        if self.position.angle is not None:
            pos.append(format_float(self.position.angle))
        expr.append(pos)

        expr.append(format_bool('fields_autoplaced', self.fieldsAutoplaced))
        expr.append(self.effects._to_sexpr_raw())
        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        for prop in self.properties:
            expr.append(prop._to_sexpr_raw())

        return expr


@dataclass
class HierarchicalLabel():
    """The ``hierarchical_label`` token defines a label that are used by hierarchical sheets to
    define connections between sheet in hierarchical designs

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_hierarchical_label_section
    """

    text: str = ""
    """The ``text`` token defines the text in the label"""

    shape: str = "input"
    """The ``shape`` token defines the way the global label is drawn. Possible values are:
    ``input``, ``output``, ``bidirectional``, ``tri_state``, ``passive``."""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` token defines the X and Y coordinates and rotation angle of the label"""

    effects: Effects = field(default_factory=lambda: Effects())
    """The ``effects`` token defines how the label is drawn"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""
    
    fieldsAutoplaced: bool = False
    """The ``fields_autoplaced`` is a flag that indicates that any PROPERTIES associated
    with the global label have been place automatically"""

    properties: list[Property] = field(default_factory=list)

    @classmethod
    def from_sexpr(cls, exp: list) -> HierarchicalLabel:
        """Convert the given S-Expresstion into a HierarchicalLabel object

        Args:
            - exp (list): Part of parsed S-Expression ``(hierarchical_label ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not hierarchical_label

        Returns:
            - HierarchicalLabel: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'hierarchical_label':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.text = exp[1]
        for item in exp[2:]:
            if is_bool_key(item, 'fields_autoplaced'): object.fieldsAutoplaced = parse_bool(item, 'fields_autoplaced')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'effects': object.effects = Effects().from_sexpr(item)
            elif item[0] == 'shape': object.shape = item[1]
            elif item[0] == 'uuid': object.uuid = item[1]
            elif item[0] == 'property': object.properties.append(Property().from_sexpr(item))
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['hierarchical_label', escape_and_quote(self.text)]

        expr.append(['shape', self.shape])

        pos = ['at', format_float(self.position.X), format_float(self.position.Y)]
        if self.position.angle is not None:
            pos.append(format_float(self.position.angle))
        expr.append(pos)

        expr.append(format_bool('fields_autoplaced', self.fieldsAutoplaced))
        expr.append(self.effects._to_sexpr_raw())
        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        for prop in self.properties:
            expr.append(prop._to_sexpr_raw())

        return expr


@dataclass
class SymbolProjectPath():
    """The symbol project path defines the ``path`` token to the sheet instance of the instance data
    of a symbol.

    Available since KiCad v7.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_symbol_section
    """
    
    sheetInstancePath: str = ""
    """The ``PATH_INSTANCE`` token defines the path to the symbol instance"""

    reference: str = ""
    """The ``reference`` token is a string that defines the reference designator for the symbol
    instance"""

    unit: int = 1
    """The ``unit`` token is a integer that defines the symbol unit for the symbol instance. For 
    symbols that do not define multiple units, this will always be 1."""

    @classmethod
    def from_sexpr(cls, exp: list) -> SymbolProjectPath:        
        """Convert the given S-Expression into a SymbolProjectPath object

        Args:
            - exp (list): Part of parsed S-Expression ``(path ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not path

        Returns:
            - SymbolProjectPath: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list) or len(exp) < 2:
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'path':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.sheetInstancePath = exp[1]
        for item in exp[2:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'reference': object.reference = item[1]
            elif item[0] == 'unit': object.unit = int(item[1])
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=4, newline=True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 4.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ['path', escape_and_quote(self.sheetInstancePath)]
        expr.append(['reference', escape_and_quote(self.reference)])
        expr.append(['unit', self.unit])
        return expr


@dataclass
class SymbolProjectInstance(ProjectInstance):
    """The ``project`` token attribute defines the name of the project as well as a list of symbol
    project paths (instance data). There can be instance data from other project when schematics 
    are shared across multiple projects. The projects will have to be sorted by the ``name`` token
    in alphabetical order.

    Available since KiCad v7.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_symbol_section
    """

    paths: List[SymbolProjectPath] = field(default_factory=list)
    """The ``paths`` token defines a list of symbol project paths for this project instance"""
    
    @classmethod
    def from_sexpr(cls, exp: list) -> SymbolProjectInstance:        
        """Convert the given S-Expression into a SymbolProjectInstance object

        Args:
            - exp (list): Part of parsed S-Expression ``(project ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not project

        Returns:
            - SymbolProjectInstance: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list) or len(exp) < 2:
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'project':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.name = exp[1]
        for item in exp[2:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'path': object.paths.append(SymbolProjectPath.from_sexpr(item))
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['project', escape_and_quote(self.name)]

        for path in self.paths:
            expr.append(path._to_sexpr_raw())

        return expr


@dataclass
class SchematicSymbol():
    """The ``symbol`` token in the symbol section of the schematic defines an instance of a symbol
    from the library symbol section of the schematic

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_symbol_section
    """

    @property
    def libId(self) -> str:
        """The ``lib_id`` token defines which symbol in the library symbol section of the schematic
        this schematic symbol references. In ``kiutils``, the ``lib_id`` token is a combination of
        both the ``libraryNickname`` and ``entryName`` token. Setting the ``lib_id`` token will
        update those tokens accordingly.

        Returns:
            - Symbol id in the following format: ``<libraryNickname>:<entryName>`` or ``<entryName>``,
              if ``libraryNickname`` token is not set.
        """
        if self.libraryNickname:
            return f'{self.libraryNickname}:{self.entryName}'
        else:
            return f'{self.entryName}'

    @libId.setter
    def libId(self, symbol_id: str):
        """Sets the ``lib_id`` token and parses its contents into the ``libraryNickname`` and
        ``entryName`` token.

        Args:
            - symbol_id (str): The symbol id in the following format: ``<libraryNickname>:<entryName>``
              or only ``<entryName>``
        """
        parse_symbol_id = re.match(r"^(.+?):(.+?)$", symbol_id)
        if parse_symbol_id:
            self.libraryNickname = parse_symbol_id.group(1)
            self.entryName = parse_symbol_id.group(2)
        else:
            self.libraryNickname = None
            self.entryName = symbol_id

    libraryNickname: Optional[str] = None
    """The optional ``libraryNickname`` token defines which symbol library this symbol belongs to
    and is a part of the ``id`` token"""

    entryName: str = None
    """The ``entryName`` token defines the actual name of the symbol and is a part of the ``id``
    token"""

    libName: Optional[str] = None
    """The optional ``lib_name`` token is only set when the symbol was edited in the schematic.
    It may be set to ``<entryName>_X`` where X is a unique number that specifies which variation
    this symbol is of its original."""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` defines the X and Y coordinates and angle of rotation of the symbol"""

    unit: Optional[int] = None
    """The optional ``unit`` token attribute defines which unit in the symbol library definition
    that the schematic symbol represents"""

    inBom: bool = False
    """The ``in_bom`` token attribute determines whether the schematic symbol appears in any bill
    of materials output"""

    onBoard: bool = False
    """The ``on_board`` token attribute determines if the footprint associated with the symbol is
    exported to the board via the netlist"""

    dnp: Optional[bool] = None
    """The optional ``dnp`` token defines if a symbol is marked as do-not-populate in the schematic. 
    
    Available since KiCad v7"""

    fieldsAutoplaced: bool = False
    """The ``fields_autoplaced`` is a flag that indicates that any PROPERTIES associated
    with the global label have been place automatically"""

    uuid: Optional[str] = ""
    """The optional `uuid` defines the universally unique identifier"""

    properties: List[Property] = field(default_factory=list)
    """The ``properties`` section defines a list of symbol properties of the schematic symbol"""

    pins: Dict[str, str] = field(default_factory=dict)
    """The ``pins`` token defines a dictionary with pin numbers in form of strings as keys and
    uuid's as values"""

    mirror: Optional[str] = None
    """The ``mirror`` token defines if the symbol is mirrored in the schematic. Accepted values:
    ``x`` or ``y``. When mirroring around the x and y axis at the same time use some additional
    rotation to get the correct orientation of the symbol."""

    instances: List[SymbolProjectInstance] = field(default_factory=list)
    """The ``instances`` token defines a list of symbol instances grouped by project. Every symbol 
    will have a least one instance.
    
    Available since KiCad v7."""

    # Available since KiCad v9

    exclude_from_sim: Optional[bool] = None
    """The ``exclude_from_sim`` token indicates that component should not be taken into account during simulation"""

    @classmethod
    def from_sexpr(cls, exp: list) -> SchematicSymbol:
        """Convert the given S-Expresstion into a SchematicSymbol object

        Args:
            - exp (list): Part of parsed S-Expression ``(symbol ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not symbol

        Returns:
            - SchematicSymbol: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'symbol':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, 'fields_autoplaced'): object.fieldsAutoplaced = parse_bool(item, 'fields_autoplaced')
            elif is_bool_key(item, 'in_bom'): object.inBom = parse_bool(item, 'in_bom')
            elif is_bool_key(item, 'on_board'): object.onBoard = parse_bool(item, 'on_board')
            elif is_bool_key(item, 'dnp'): object.dnp = parse_bool(item, 'dnp')
            elif is_bool_key(item, 'exclude_from_sim'): object.exclude_from_sim = parse_bool(item, 'exclude_from_sim')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'lib_id': object.libId = item[1]
            elif item[0] == 'lib_name': object.libName = item[1]
            elif item[0] == 'uuid': object.uuid = item[1]
            elif item[0] == 'unit': object.unit = int(item[1])
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'property': object.properties.append(Property().from_sexpr(item))
            elif item[0] == 'pin': object.pins.update({item[1]: item[2][1]})
            elif item[0] == 'mirror': object.mirror = item[1]
            elif item[0] == 'instances':
                for instance in item[1:]: object.instances.append(SymbolProjectInstance.from_sexpr(instance))
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['symbol']

        if self.libName is not None:
            expr.append(['lib_name', escape_and_quote(self.libName)])

        expr.append(['lib_id', escape_and_quote(self.libId)])

        pos = ['at', format_float(self.position.X), format_float(self.position.Y)]
        if self.position.angle is not None:
            pos.append(format_float(self.position.angle))
        expr.append(pos)

        if self.mirror is not None:
            expr.append(['mirror', self.mirror])

        if self.unit is not None:
            expr.append(['unit', self.unit])

        if self.exclude_from_sim is not None:
            expr.append(format_bool("exclude_from_sim", self.exclude_from_sim, compact=False, yesno=True))

        expr.append(format_bool("in_bom", self.inBom, compact=False, yesno=True))
        expr.append(format_bool("on_board", self.onBoard, compact=False, yesno=True))
        if self.dnp is not None:
            expr.append(format_bool("dnp", self.dnp, compact=False, yesno=True))
        expr.append(format_bool("fields_autoplaced", self.fieldsAutoplaced))

        if self.uuid:
            expr.append(['uuid', quote(self.uuid)])

        for prop in self.properties:
            expr.append(prop._to_sexpr_raw())

        for number, uuid in self.pins.items():
            expr.append(['pin', escape_and_quote(number), ['uuid', quote(uuid)]])

        if len(self.instances) != 0:
            instances_expr = ['instances']
            for instance in self.instances:
                instances_expr.append(instance._to_sexpr_raw())
            expr.append(instances_expr)

        return expr


@dataclass
class HierarchicalPin():
    """The ``pin`` token in a sheet object defines an electrical connection between the sheet in a
       schematic with the hierarchical label defined in the associated schematic file

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_hierarchical_sheet_pin_definition
    """

    name: str = ""
    """	The ``name`` attribute defines the name of the sheet pin. It must have an identically named
        hierarchical label in the associated schematic file."""

    connectionType: str = "input"
    """The electrical connect type token defines the type of electrical connect made by the
       sheet pin"""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` defines the X and Y coordinates and angle of rotation of the pin"""

    effects: Effects = field(default_factory=lambda: Effects())
    """The ``effects`` section defines how the pin name text is drawn"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    @classmethod
    def from_sexpr(cls, exp: list) -> HierarchicalPin:
        """Convert the given S-Expresstion into a HierarchicalPin object

        Args:
            - exp (list): Part of parsed S-Expression ``(pin ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not pin

        Returns:
            - HierarchicalPin: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'pin':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.name = exp[1]
        object.connectionType = exp[2]
        for item in exp[3:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'effects': object.effects = Effects().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=4, newline=True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 4.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ['pin', escape_and_quote(self.name), self.connectionType]

        pos = ['at', format_float(self.position.X), format_float(self.position.Y)]
        if self.position.angle is not None:
            pos.append(format_float(self.position.angle))
        expr.append(pos)

        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        expr.append(self.effects._to_sexpr_raw())
        return expr


@dataclass
class HierarchicalSheetProjectPath():
    """The symbol project path defines the ``path`` token to the sheet instance of the instance data
    of a symbol.

    Available since KiCad v7.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_hierarchical_sheet_section
    """
    
    sheetInstancePath: str = ""
    """The ``PATH_INSTANCE`` token defines the path to the symbol instance"""

    page: str = ""
    """The ``page`` token is a string that defines the page number of the sheet instance"""

    @classmethod
    def from_sexpr(cls, exp: list) -> HierarchicalSheetProjectPath:        
        """Convert the given S-Expression into a HierarchicalSheetProjectPath object

        Args:
            - exp (list): Part of parsed S-Expression ``(path ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not path

        Returns:
            - HierarchicalSheetProjectPath: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list) or len(exp) < 2:
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'path':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.sheetInstancePath = exp[1]
        for item in exp[2:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'page': object.page = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=4, newline=True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 4.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        return ['path', escape_and_quote(self.sheetInstancePath), ['page', escape_and_quote(self.page)]]


@dataclass
class HierarchicalSheetProjectInstance(ProjectInstance):
    """The ``project`` token attribute defines the name of the project as well as a list of 
    hierarchical sheet project paths (instance data). There can be instance data from other project 
    when schematics are shared across multiple projects. The projects will have to be sorted by the 
    ``name`` token in alphabetical order.

    Available since KiCad v7.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_hierarchical_sheet_section
    """

    paths: List[HierarchicalSheetProjectPath] = field(default_factory=list)
    """The ``paths`` token defines a list of hierarchical sheet project paths for this project instance"""
    
    @classmethod
    def from_sexpr(cls, exp: list) -> HierarchicalSheetProjectInstance:        
        """Convert the given S-Expression into a HierarchicalSheetProjectInstance object

        Args:
            - exp (list): Part of parsed S-Expression ``(project ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not project

        Returns:
            - HierarchicalSheetProjectInstance: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list) or len(exp) < 2:
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'project':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.name = exp[1]
        for item in exp[2:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'path': object.paths.append(HierarchicalSheetProjectPath.from_sexpr(item))
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['project', escape_and_quote(self.name)]

        for path in self.paths:
            expr.append(path._to_sexpr_raw())

        return expr


@dataclass
class HierarchicalSheet():
    """The ``sheet`` token defines a hierarchical sheet of the schematic

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_hierarchical_sheet_section
    """

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` defines the X and Y coordinates and angle of rotation of the sheet in the schematic"""

    width: float = 0
    """The ``width`` token defines the width of the sheet"""

    height: float = 0
    """The ``height`` token defines the height of the sheet"""

    fieldsAutoplaced: bool = False
    """The ``fields_autoplaced`` is a flag that indicates that any PROPERTIES associated
       with the global label have been place automatically"""

    stroke: Stroke = field(default_factory=lambda: Stroke())
    """The ``stroke`` defines how the sheet outline is drawn"""

    fill: ColorRGBA = field(default_factory=lambda: ColorRGBA())
    """The fill defines the color how the sheet is filled"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    sheetName: Property = field(default_factory=lambda: Property(key="Sheet name"))
    """The ``sheetName`` is a property that defines the name of the sheet. The property's
       key should therefore be set to `Sheet name`"""

    fileName: Property = field(default_factory=lambda: Property(key="Sheet file"))
    """The ``fileName`` is a property that defines the file name of the sheet. The property's
       key should therefore be set to `Sheet file`"""

    properties: List[Property] = field(default_factory=list)
    """The ``properties`` section defines a list of properties defined for the hiererchical sheet.
       This holds all properties except that held by ``sheetName`` and ``fileName`` members."""

    pins: List[HierarchicalPin] = field(default_factory=list)
    """The ``pins`` section is a list of hierarchical pins that map a hierarchical label defined in
       the associated schematic file"""
    
    instances: List[HierarchicalSheetProjectInstance] = field(default_factory=list)
    """The ``instances`` token defines a list of hierachical sheet instances grouped by project. 
    Every hierarchical sheet will have a least one instance.
    
    Available since KiCad v7."""

    # Available since KiCad v9

    exclude_from_sim: Optional[bool] = None
    """The optional ``exclude_from_sim`` token defines if all components in this sheet are excluded from simulation"""

    in_bom: Optional[bool] = None
    """The optional ``in_bom`` token defines if all components in this sheet are included in BOM"""

    on_board: Optional[bool] = None
    """The optional ``on_board`` token defines if all components in this sheet are included on PCB"""

    dnp: Optional[bool] = None
    """The optional ``dnp`` token defines if all components in this sheet are DNP"""

    @classmethod
    def from_sexpr(cls, exp: list) -> HierarchicalSheet:
        """Convert the given S-Expresstion into a HierarchicalSheet object

        Args:
            - exp (list): Part of parsed S-Expression ``(sheet ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not sheet

        Returns:
            - HierarchicalSheet: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'sheet':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, 'fields_autoplaced'): object.fieldsAutoplaced = parse_bool(item, 'fields_autoplaced')
            elif is_bool_key(item, 'exclude_from_sim'): object.exclude_from_sim = parse_bool(item, 'exclude_from_sim')
            elif is_bool_key(item, 'in_bom'): object.in_bom = parse_bool(item, 'in_bom')
            elif is_bool_key(item, 'on_board'): object.on_board = parse_bool(item, 'on_board')
            elif is_bool_key(item, 'dnp'): object.dnp = parse_bool(item, 'dnp')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'at': object.position = Position().from_sexpr(item)
            elif item[0] == 'stroke': object.stroke = Stroke().from_sexpr(item)
            elif item[0] == 'size':
                object.width, object.height = item[1], item[2]
            elif item[0] == 'fill':
                object.fill = ColorRGBA().from_sexpr(item[1])
                object.fill.precision = 4
            elif item[0] == 'uuid': object.uuid = item[1]
            elif item[0] == 'property':
                p = Property().from_sexpr(item)
                if item[1] in ['Sheet name', 'Sheetname']: object.sheetName = p
                elif item[1] in ['Sheet file', 'Sheetfile']: object.fileName = p
                else: object.properties.append(p)
            elif item[0] == 'pin': object.pins.append(HierarchicalPin().from_sexpr(item))
            elif item[0] == 'instances':
                for instance in item[1:]: object.instances.append(HierarchicalSheetProjectInstance.from_sexpr(instance))
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
            'sheet',
            ['at', format_float(self.position.X), format_float(self.position.Y)],
            ['size', format_float(self.width), format_float(self.height)],
        ]

        if self.exclude_from_sim is not None:
            expr.append(format_bool('exclude_from_sim', self.exclude_from_sim, compact=False, yesno=True))
        if self.in_bom is not None:
            expr.append(format_bool('in_bom', self.in_bom, compact=False, yesno=True))
        if self.on_board is not None:
            expr.append(format_bool('on_board', self.on_board, compact=False, yesno=True))
        if self.dnp is not None:
            expr.append(format_bool('dnp', self.dnp, compact=False, yesno=True))

        expr.append(format_bool('fields_autoplaced', self.fieldsAutoplaced))

        expr.append(self.stroke._to_sexpr_raw())
        expr.append(['fill', self.fill._to_sexpr_raw()])
        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        expr.append(self.sheetName._to_sexpr_raw())
        expr.append(self.fileName._to_sexpr_raw())

        for p in self.properties:
            expr.append(p._to_sexpr_raw())

        for pin in self.pins:
            expr.append(pin._to_sexpr_raw())

        if len(self.instances) != 0:
            instances_expr = ['instances']
            for instance in self.instances:
                instances_expr.append(instance._to_sexpr_raw())
            expr.append(instances_expr)

        return expr


@dataclass
class HierarchicalSheetInstance():
    """The sheet_instance token defines the per sheet information for the entire schematic. This
       section will only exist in schematic files that are the root sheet of a project

    Documentation:
           https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_hierarchical_sheet_instance_section
    """

    instancePath: str = "/"
    """The ``instancePath`` attribute is the path to the sheet instance"""

    page: str = "1"
    """The ``page`` token defines the page number of the schematic represented by the sheet
       instance information. Page numbers can be any valid string."""

    @classmethod
    def from_sexpr(cls, exp: list) -> HierarchicalSheetInstance:
        """Convert the given S-Expresstion into a HierarchicalSheetInstance object

        Args:
            - exp (list): Part of parsed S-Expression ``(path ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not path

        Returns:
            - HierarchicalSheetInstance: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'path':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.instancePath = exp[1]
        for item in exp[2:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'page': object.page = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=4, newline=True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 4.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        return ['path', escape_and_quote(self.instancePath), ['page', escape_and_quote(self.page)]]


@dataclass
class SymbolInstance():
    """The ``symbol_instance`` token defines the per symbol information for the entire schematic

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/#_symbol_instance_section
    """

    path: str = "/"
    """The ``path`` attribute is the path to the sheet instance"""

    reference: str = ""
    """The ``reference`` token attribute is a string that defines the reference designator for
       the symbol instance"""

    unit: int = 0
    """The unit token attribute is a integer ordinal that defines the symbol unit for the
       symbol instance. For symbols that do not define multiple units, this will always be 1."""

    value: str = ""
    """The value token attribute is a string that defines the value field for the symbol instance"""

    footprint: str = ""
    """The ``footprint`` token attribute is a string that defines the LIBRARY_IDENTIFIER for footprint associated with the symbol instance"""

    @classmethod
    def from_sexpr(cls, exp: list) -> SymbolInstance:
        """Convert the given S-Expresstion into a SymbolInstance object

        Args:
            - exp (list): Part of parsed S-Expression ``(path ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not path

        Returns:
            - SymbolInstance: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'path':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.path = exp[1]
        for item in exp[2:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'reference': object.reference = item[1]
            elif item[0] == 'unit': object.unit = int(item[1])
            elif item[0] == 'value': object.value = item[1]
            elif item[0] == 'footprint': object.footprint = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=4, newline=True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 4.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        return [
            'path', escape_and_quote(self.path),
            ['reference', escape_and_quote(self.reference)],
            ['unit', self.unit],
            ['value', escape_and_quote(self.value)],
            ['footprint', escape_and_quote(self.footprint)],
        ]


@dataclass
class Rectangle():
    """The ``rectangle`` token defines a graphical rectangle in a schematic.

    Available since KiCad v7

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_symbol_rectangle
    """

    start: Position = field(default_factory=lambda: Position())
    """The ``start`` token attributes define the coordinates of the start point of the rectangle"""

    end: Position = field(default_factory=lambda: Position())
    """The ``end`` token attributes define the coordinates of the end point of the rectangle"""

    stroke: Stroke = field(default_factory=lambda: Stroke())
    """The ``stroke`` defines how the rectangle outline is drawn"""

    fill: Fill = field(default_factory=lambda: Fill())
    """The ``fill`` token attributes define how rectangle arc is filled"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Rectangle:
        """Convert the given S-Expresstion into a Rectangle object

        Args:
            - exp (list): Part of parsed S-Expression ``(rectangle ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not rectangle

        Returns:
            - Rectangle: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'rectangle':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'start': object.start = Position().from_sexpr(item)
            elif item[0] == 'end': object.end = Position().from_sexpr(item)
            elif item[0] == 'stroke': object.stroke = Stroke().from_sexpr(item)
            elif item[0] == 'fill': object.fill = Fill().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
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
            'rectangle',
            ['start', format_float(self.start.X), format_float(self.start.Y)],
            ['end', format_float(self.end.X), format_float(self.end.Y)],
        ]

        expr.append(self.stroke._to_sexpr_raw())
        expr.append(self.fill._to_sexpr_raw())

        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        return expr


@dataclass
class Arc():
    """The ``Arc`` token defines a graphical arc in a schematic.

    Available since KiCad v7

    Documentation:
        - ???
    """

    start: Position = field(default_factory=lambda: Position())
    """The ``start`` token attributes define the coordinates of the start point of the arc"""

    mid: Position = field(default_factory=lambda: Position())
    """The ``end`` token attributes define the coordinates of the mid point of the arc"""

    end: Position = field(default_factory=lambda: Position())
    """The ``end`` token attributes define the coordinates of the end point of the arc"""

    stroke: Stroke = field(default_factory=lambda: Stroke())
    """The ``stroke`` defines how the arc outline is drawn"""

    fill: Fill = field(default_factory=lambda: Fill())
    """The ``fill`` token attributes define how the arc is filled"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Arc:
        """Convert the given S-Expresstion into a Arc object

        Args:
            - exp (list): Part of parsed S-Expression ``(arc ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not arc

        Returns:
            - Arc: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'arc':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'start': object.start = Position().from_sexpr(item)
            elif item[0] == 'mid': object.mid = Position().from_sexpr(item)
            elif item[0] == 'end': object.end = Position().from_sexpr(item)
            elif item[0] == 'stroke': object.stroke = Stroke().from_sexpr(item)
            elif item[0] == 'fill': object.fill = Fill().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
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
            'arc',
            ['start', format_float(self.start.X), format_float(self.start.Y)],
            ['mid', format_float(self.mid.X), format_float(self.mid.Y)],
            ['end', format_float(self.end.X), format_float(self.end.Y)],
        ]

        expr.append(self.stroke._to_sexpr_raw())
        expr.append(self.fill._to_sexpr_raw())

        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        return expr


@dataclass
class Circle():
    """The ``Circle`` token defines a graphical circle in a schematic.

    Available since KiCad v7

    Documentation:
        - ???
    """

    center: Position = field(default_factory=lambda: Position())
    """The ``center`` token attributes define the coordinates of the center point of the circle"""

    radius: float = 0.0
    """The ``radius`` token attributes define the radius of the circle"""

    stroke: Stroke = field(default_factory=lambda: Stroke())
    """The ``stroke`` defines how the circle outline is drawn"""

    fill: Fill = field(default_factory=lambda: Fill())
    """The ``fill`` token attributes define how the circle is filled"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Circle:
        """Convert the given S-Expresstion into a Circle object

        Args:
            - exp (list): Part of parsed S-Expression ``(circle ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not circle

        Returns:
            - Circle: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'circle':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'center': object.center = Position().from_sexpr(item)
            elif item[0] == 'radius': object.radius = item[1]
            elif item[0] == 'stroke': object.stroke = Stroke().from_sexpr(item)
            elif item[0] == 'fill': object.fill = Fill().from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
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
            'circle',
            ['center', format_float(self.center.X), format_float(self.center.Y)],
            ['radius', format_float(self.radius)],
        ]

        expr.append(self.stroke._to_sexpr_raw())
        expr.append(self.fill._to_sexpr_raw())

        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        return expr


@dataclass
class NetclassFlag():
    """The ``netclass_flag`` token defines a netclass flag in a schematic.

    Available since KiCad v7

    Documentation:
        - ???
    """

    text: str = ""
    """The ``text`` token defines the text the netclass flag"""

    length: float = 2.54
    """The ``length`` token defines the length of the netclass flag"""

    shape: str = "round"
    """The ``shape`` token defines the shape of the netclass flag. Valid values are ``round``,
    ``rectangle``, ``dot`` or``diamond``."""

    position: Position = field(default_factory=lambda: Position)
    """The ``position`` token defines the position and rotation of the netclass flag"""

    effects: Effects = field(default_factory=lambda: Effects)
    """The ``effects`` token defines how the text is drawn"""

    properties: List[Property] = field(default_factory=list)
    """The ``properties`` token defines a list of properties the netclass is assigned to"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier"""

    fieldsAutoplaced: bool = False
    """The ``fields_autoplaced`` is a flag that indicates that any PROPERTIES associated
    with the netclas flag have been place automatically"""

    @classmethod
    def from_sexpr(cls, exp: list) -> NetclassFlag:
        """Convert the given S-Expresstion into a Circle object

        Args:
            - exp (list): Part of parsed S-Expression ``(netclass_flag ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not netclass_flag

        Returns:
            - NetclassFlag: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'netclass_flag':
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.text = exp[1]
        for item in exp[2:]:
            if is_bool_key(item, 'fields_autoplaced'): object.fieldsAutoplaced = parse_bool(item, 'fields_autoplaced')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'length': object.length = item[1]
            elif item[0] == 'shape': object.shape = item[1]
            elif item[0] == 'at': object.position = Position.from_sexpr(item)
            elif item[0] == 'effects': object.effects = Effects.from_sexpr(item)
            elif item[0] == 'uuid': object.uuid = item[1]
            elif item[0] == 'property': object.properties.append(Property.from_sexpr(item))
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
        pos = ['at', format_float(self.position.X), format_float(self.position.Y)]
        if self.position.angle is not None:
            pos.append(format_float(self.position.angle))

        expr = [
            'netclass_flag', escape_and_quote(self.text),
            ['length', format_float(self.length)],
            ['shape', self.shape],
            pos,
            format_bool('fields_autoplaced', self.fieldsAutoplaced),
        ]

        expr.append(self.effects._to_sexpr_raw())

        if self.uuid is not None:
            expr.append(['uuid', quote(self.uuid)])

        for prop in self.properties:
            expr.append(prop._to_sexpr_raw())

        return expr


@dataclass
class TableBorder:
    external: bool = False
    """The External border controls whether there is a border drawn around the entire table."""

    header: bool = False
    """The Header border controls whether there is a border drawn around the cells in the top row."""

    stroke: Optional[Stroke] = None

    @classmethod
    def from_sexpr(cls, exp: list) -> TableBorder:
        """Convert the given S-Expresstion into a TableBorder object

        Args:
            - exp (list): Part of parsed S-Expression ``(border ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not border

        Returns:
            - TableBorder: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'border':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, 'external'): object.external = parse_bool(item, 'external')
            elif is_bool_key(item, 'header'): object.header = parse_bool(item, 'header')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'stroke': object.stroke = Stroke().from_sexpr(item)
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['border']

        expr.append(format_bool('external', self.external))
        expr.append(format_bool('header', self.header))

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        return expr


@dataclass
class TableSeparators:
    rows: bool = False
    """The Row Lines enable horizontal lines between rows."""

    columns: bool = False
    """The Row Lines enable vertical lines between columns."""

    stroke: Optional[Stroke] = None

    @classmethod
    def from_sexpr(cls, exp: list) -> TableSeparators:
        """Convert the given S-Expresstion into a TableSeparators object

        Args:
            - exp (list): Part of parsed S-Expression ``(separators ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not separator

        Returns:
            - TableSeparators: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'separators':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, 'rows'): object.rows = parse_bool(item, 'rows')
            elif is_bool_key(item, 'cols'): object.columns = parse_bool(item, 'cols')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'stroke': object.stroke = Stroke().from_sexpr(item)
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['separators']

        expr.append(format_bool('rows', self.rows))
        expr.append(format_bool('cols', self.columns))

        if self.stroke is not None:
            expr.append(self.stroke._to_sexpr_raw())

        return expr


@dataclass
class Table():
    """The ``table`` token defines a table

    Documentation:
        https://docs.kicad.org/9.0/en/eeschema/eeschema.html#tables
    """

    column_count: int = 0
    """The ``column_count`` token defines the number of columns in the table"""

    border: Optional[TableBorder] = None
    """The ``border`` token defines the border of the table"""

    separators: Optional[TableSeparators] = None
    """The ``separators`` token defines the separators of the table"""

    column_widths: List[float] = field(default_factory=list)
    """The ``column_widths`` token defines the widths of the columns in the table"""

    row_heights: List[float] = field(default_factory=list)
    """The ``row_heights`` token defines the heights of the rows in the table"""

    cells: List[TextBox] = field(default_factory=list)
    """The ``cells`` token defines the cells in the table"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Table:
        """Convert the given S-Expresstion into a Table object

        Args:
            - exp (list): Part of parsed S-Expression ``(table ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not table

        Returns:
            - Table: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'table':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'column_count': object.column_count = int(item[1])
            elif item[0] == 'border': object.border = TableBorder().from_sexpr(item)
            elif item[0] == 'separators': object.separators = TableSeparators().from_sexpr(item)
            elif item[0] == 'column_widths':
                for width in item[1:]: object.column_widths.append(float(width))
            elif item[0] == 'row_heights':
                for height in item[1:]: object.row_heights.append(float(height))
            elif item[0] == 'cells':
                for cell in item[1:]: object.cells.append(TextBox.from_sexpr(cell, table_cell=True))
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent=2, newline=True) -> str:
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
        expr = ['table']

        expr.append(['column_count', self.column_count])

        if self.border is not None:
            expr.append(self.border._to_sexpr_raw())

        if self.separators is not None:
            expr.append(self.separators._to_sexpr_raw())

        expr.append(['column_widths'] + [format_float(w) for w in self.column_widths])
        expr.append(['row_heights'] + [format_float(h) for h in self.row_heights])

        if self.cells:
            cells_expr = ['cells']
            for cell in self.cells:
                cells_expr.append(cell._to_sexpr_raw(table_cell=True))
            expr.append(cells_expr)

        return expr