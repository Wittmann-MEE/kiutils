"""The zone token defines a zone on the board or footprint. Zones serve two purposes in
   KiCad: filled copper zones and keep out areas.

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0

Major changes:
    11.02.2022 - created

Documentation taken from:
    https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_footprint_graphics_items
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List

from enum import IntEnum

from kiutils.items.brditems import Arc
from kiutils.items.common import Position
from kiutils.utils.string_utils import *
from kiutils.utils.parsing_utils import *
from kiutils.utils.sexpr import sexp_to_string

@dataclass
class KeepoutSettings():
    """The ``keepout `` token attributes define which objects should be kept out of the
    zone. This section only applies to keep out zones.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_zone_keep_out_settings
    """

    tracks: str = "allowed"
    """The ``tracks`` token attribute defines whether or not tracks should be excluded
    from the keep out area. Valid attributes are ``allowed`` and ``not_allowed``."""

    vias: str = "allowed"
    """The ``vias`` token attribute defines whether or not vias should be excluded from
    the keep out area. Valid attributes are ``allowed`` and ``not_allowed``."""

    pads: str = "allowed"
    """The ``pads`` token attribute defines whether or not pads should be excluded from
    the keep out area. Valid attributes are ``allowed`` and ``not_allowed``."""

    copperpour: str = "not-allowed"
    """The ``copperpour`` token attribute defines whether or not copper pours should be
    excluded from the keep out area. Valid attributes are ``allowed`` and ``not_allowed``."""

    footprints: str = "not-allowed"
    """The ``footprints`` token attribute defines whether or not footprints should be
    excluded from the keep out area. Valid attributes are ``allowed`` and ``not_allowed``."""

    @classmethod
    def from_sexpr(cls, exp: list) -> KeepoutSettings:
        """Convert the given S-Expresstion into a KeepoutSettings object

        Args:
            - exp (list): Part of parsed S-Expression ``(keepout ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not keepout

        Returns:
            - KeepoutSettings: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'keepout':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'tracks': object.tracks = item[1]
            elif item[0] == 'vias': object.vias = item[1]
            elif item[0] == 'pads': object.pads = item[1]
            elif item[0] == 'copperpour': object.copperpour = item[1]
            elif item[0] == 'footprints': object.footprints = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 0, newline: bool = False) -> str:
        """Generate the S-Expression representing this object. When no coordinates are set
        in the curve, the resulting S-Expression will be left empty.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to False.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        return [
            'keepout',
            ['tracks', self.tracks],
            ['vias', self.vias],
            ['pads', self.pads],
            ['copperpour', self.copperpour],
            ['footprints', self.footprints],
        ]


@dataclass
class FillSettings():
    """The ``fill`` token attributes define how the zone is to be filled.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_zone_fill_settings
    """

    yes: bool = False
    """The ``yes`` token specifies if the zone should be filled. If not specified, the zone is
    not filled and no additional attributes are required."""

    mode: Optional[str] = None
    """The optional ``mode`` token attribute defines how the zone is filled. The only valid fill
    mode is ``hatched``. When not defined, the fill mode is solid."""

    thermalGap: Optional[float] = None
    """The optional ``thermalGap`` token attribute defines the distance from the zone to all
    pad thermal relief connections to the zone."""

    thermalBridgeWidth: Optional[float] = None
    """The optional ``thermalBridgeWidth`` token attribute defines the spoke width for all
    pad thermal relief connection to the zone."""

    smoothingStyle: Optional[str] = None
    """The optional ``smoothingStyle`` token attributes define the style of corner smoothing. Valid
    smoothing styles are ``chamfer`` and ``fillet``"""

    smoothingRadius: Optional[float] = None
    """The optional ``smoothingRadius`` token attributes define the radius of corner smoothing"""

    islandRemovalMode: Optional[int] = None
    """The optional ``islandRemovalMode`` token attribute defines the island removal mode.
    Valid island removal modes are:
    - 0: Always remove islands.
    - 1: Never remove islands.
    - 2: Minimum area island to allow.
    """

    islandAreaMin: Optional[float] = None
    """The optional ``islandAreaMin`` token attribute defines the minimum allowable zone
      island. This only valid when the remove islands mode is set to 2."""

    hatchThickness: Optional[float] = None
    """The optional ``hatchThickness`` token attribute defines the thickness for hatched fills"""

    hatchGap: Optional[float] = None
    """The optional ``hatchGap`` token attribute defines the distance between lines for hatched
    fills"""

    hatchOrientation: Optional[float] = None
    """The optional ``hatchOrientation`` token attribute defines the line angle for hatched fills"""

    hatchSmoothingLevel: Optional[int] = None
    """The optional ``hatchSmoothingLevel`` token attribute defines how hatch outlines are
    smoothed. Valid hatch smoothing levels are:
    - 0: No smoothing
    - 1: Fillet
    - 2: Arc minimum
    - 3: Arc maximum
    """

    hatchSmoothingValue: Optional[float] = None
    """The optional ``hatchSmoothingValue`` token attribute defines the ratio between the hole
    and the chamfer/fillet size"""

    hatchBorderAlgorithm: Optional[int] = None
    """The optional ``hatchBorderAlgorithm`` token attribute defines the if the zone line
    thickness is used when performing a hatch fill. Valid values for the hatch border
    algorithm are:
    - 0: Use zone minimum thickness.
    - 1: Use hatch thickness.
    """

    hatchMinHoleArea: Optional[float] = None
    """The optional ``hatchMinHoleArea`` token attribute defines the minimum area a hatch file hole can be"""

    @classmethod
    def from_sexpr(cls, exp: list) -> FillSettings:
        """Convert the given S-Expresstion into a FillSettings object

        Args:
            - exp (list): Part of parsed S-Expression ``(fill ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not fill

        Returns:
            - FillSettings: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'fill':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, 'yes'): object.yes = parse_bool(item, 'yes')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'mode': object.mode = item[1]
            elif item[0] == 'thermal_gap': object.thermalGap = item[1]
            elif item[0] == 'thermal_bridge_width': object.thermalBridgeWidth = item[1]
            elif item[0] == 'smoothing': object.smoothingStyle = item[1]
            elif item[0] == 'radius': object.smoothingRadius = item[1]
            elif item[0] == 'island_removal_mode': object.islandRemovalMode = int(item[1])
            elif item[0] == 'island_area_min': object.islandAreaMin = item[1]
            elif item[0] == 'hatch_thickness': object.hatchThickness = item[1]
            elif item[0] == 'hatch_gap': object.hatchGap = item[1]
            elif item[0] == 'hatch_orientation': object.hatchOrientation = item[1]
            elif item[0] == 'hatch_smoothing_level': object.hatchSmoothingLevel = int(item[1])
            elif item[0] == 'hatch_smoothing_value': object.hatchSmoothingValue = item[1]
            elif item[0] == 'hatch_border_algorithm': object.hatchBorderAlgorithm = int(item[1])
            elif item[0] == 'hatch_min_hole_area': object.hatchMinHoleArea = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 0, newline: bool = False) -> str:
        """Generate the S-Expression representing this object. When no coordinates are set
        in the curve, the resulting S-Expression will be left empty.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to False.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ['fill']

        if self.yes:
            expr.append('yes')

        if self.mode is not None:
            expr.append(['mode', self.mode])

        expr.append(['thermal_gap', self.thermalGap])
        expr.append(['thermal_bridge_width', self.thermalBridgeWidth])

        if self.smoothingStyle is not None:
            expr.append(['smoothing', self.smoothingStyle])

        if self.smoothingRadius is not None:
            expr.append(['radius', self.smoothingRadius])

        if self.islandRemovalMode is not None:
            expr.append(['island_removal_mode', self.islandRemovalMode])

        if self.islandAreaMin is not None:
            expr.append(['island_area_min', self.islandAreaMin])

        if self.hatchThickness is not None:
            expr.append(['hatch_thickness', self.hatchThickness])

        if self.hatchGap is not None:
            expr.append(['hatch_gap', self.hatchGap])

        if self.hatchOrientation is not None:
            expr.append(['hatch_orientation', self.hatchOrientation])

        if self.hatchSmoothingLevel is not None:
            expr.append(['hatch_smoothing_level', self.hatchSmoothingLevel])

        if self.hatchSmoothingValue is not None:
            expr.append(['hatch_smoothing_value', self.hatchSmoothingValue])

        if self.hatchBorderAlgorithm is not None:
            expr.append(['hatch_border_algorithm', self.hatchBorderAlgorithm])

        if self.hatchMinHoleArea is not None:
            expr.append(['hatch_min_hole_area', self.hatchMinHoleArea])

        return expr


@dataclass
class ZonePolygon():
    """The ``polygon`` token defines a list of coordinates that define part of a zone"""

    coordinates: Union[List[Position], List[Arc]] = field(default_factory=list)
    """The ``coordinates`` defines the list of polygon X/Y coordinates or arcs used to define the zone polygon"""

    @classmethod
    def from_sexpr(cls, exp: list) -> ZonePolygon:
        """Convert the given S-Expresstion into a ZonePolygon object

        Args:
            - exp (list): Part of parsed S-Expression ``(polygon ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not polygon

        Returns:
            - ZonePolygon: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'polygon':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'pts':
                if all(p[0] == 'xy' for p in item[1:]):
                    object.coordinates = [Position().from_sexpr(p) for p in item[1:]]
                elif all(p[0] == 'arc' for p in item[1:]):
                    object.coordinates = [Arc().from_sexpr(p) for p in item[1:]]
                else:
                    raise ValueError(f"Expected all points to be either 'xy' or 'arc', got mixed types. Full expression: {item}")
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 4, newline: bool = True) -> str:
        """Generate the S-Expression representing this object. When no coordinates are set
        in the polygon, the resulting S-Expression will be left empty.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 4.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object. If the polygon has no coordinates, an empty
                   expression is returned.
        """
        if len(self.coordinates) == 0:
            return ''

        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        if not self.coordinates:
            return ['polygon', ['pts']]

        pts = []
        first_item = self.coordinates[0]
        if isinstance(first_item, Position):
            # All items are Position
            pts = [['xy', p.X, p.Y] for p in self.coordinates]
        elif isinstance(first_item, Arc):
            # All items are Arc
            pts = [arc._to_sexpr_raw(zone_poly=True) for arc in self.coordinates]
        else:
            raise TypeError(f'Unexpected type in coordinates: {type(first_item)}')

        return ['polygon', ['pts'] + pts]



@dataclass
class FilledPolygon():
    """The ``filled_polygon`` token defines the polygons used to fill a zone

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_zone_fill_polygons
    """

    layer: str = "F.Cu"
    """The ``layer`` token attribute defines the canonical layer the zone fill resides on"""

    # TODO: What is the definiton of this token?
    island: bool = False
    """The ``island`` token's definition has to be defined .."""

    coordinates: List[Position] = field(default_factory=list)
    """The ``coordinates`` defines the list of polygon X/Y coordinates used to fill the zone"""

    @classmethod
    def from_sexpr(cls, exp: list) -> FilledPolygon:
        """Convert the given S-Expresstion into a FilledPolygon object

        Args:
            - exp (list): Part of parsed S-Expression ``(filled_polygon ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not filled_polygon

        Returns:
            - FilledPolygon: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'filled_polygon':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, 'island'): object.island = parse_bool(item, 'island')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'layer': object.layer = item[1]
            elif item[0] == 'pts':
                for position in item[1:]: object.coordinates.append(Position().from_sexpr(position))
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 4, newline: bool = True) -> str:
        """Generate the S-Expression representing this object. When no coordinates are set
        in the filled polygon, the resulting S-Expression will be left empty.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 4.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object. If the filled polygon has no coordinates, an empty
                   expression is returned.
        """
        if len(self.coordinates) == 0:
            return ''

        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ['filled_polygon', ['layer', escape_and_quote(self.layer)]]

        if self.island:
            expr.append(format_bool('island', self.island, compact=True))

        pts = [['xy', point.X, point.Y] for point in self.coordinates]
        expr.append(['pts'] + pts)

        return expr


# TODO: This is KiCad 4 stuff, has to be tested yet ..
@dataclass
class FillSegments():
    """The ``fill_polygon`` token defines the segments used to fill the zone. This is only
       used when loading boards prior to version 4 which filled zones with segments.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_zone_fill_segments
    """

    layer: str = "F.Cu"
    """The ``layer`` token attribute defines the canonical layer the zone fill resides on"""

    coordinates: List[Position] = field(default_factory=list)
    """The ``coordinates`` defines the list of polygon X/Y coordinates used to fill the zone."""

    @classmethod
    def from_sexpr(cls, exp: list) -> FillSegments:
        """Convert the given S-Expresstion into a FillSegments object

        Args:
            - exp (list): Part of parsed S-Expression ``(fill_segments ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not fill_segments

        Returns:
            - FillSegments: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'fill_segments':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'layer': object.layer = item[1]
            elif item[0] == 'pts':
                for position in item[1:]: object.coordinates.append(Position().from_sexpr(position))
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 4, newline: bool = True) -> str:
        """Generate the S-Expression representing this object. When no coordinates are set
        in the curve, the resulting S-Expression will be left empty.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 4.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object. If the fill segments has no coordinates, an empty
              expression is returned.
        """
        if len(self.coordinates) == 0:
            return ''

        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        pts = [['xy', point.X, point.Y] for point in self.coordinates]
        return [
            'fill_segments',
            ['layer', escape_and_quote(self.layer)],
            ['pts'] + pts,
        ]


@dataclass
class Hatch():
    """Data wrapper for Zone class hatching attribute"""

    style: str = "none"
    """The ``style`` token defines the style of the hatching. Valid hatch styles are ``none``, ``edge``
    and ``full``"""

    pitch: float = 0.0
    """The ``pitch`` token defines the pitch of the hatch"""

@dataclass
class Zone():
    """The ``zone`` token defines a zone on the board or footprint. Zones serve two purposes
       in KiCad: filled copper zones and keep out areas.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_zone

    """
    locked: bool = False
    """The ``locked`` token defines if the zone may be edited or not (Missing in KiCad
    docu as of 11.02.2022)"""

    net: int = 0
    """The ``net`` token attribute defines by the net ordinal number which net in the nets
    section that the zone is part of"""

    netName: str = "unknown"
    """The ``net_name`` token attribute defines the name of the net if the zone is not a keep
    out area. The net name attribute will be an empty string if the zone is a keep out area."""

    layers: List[str] = field(default_factory=list)
    """The ``layers`` token define the canonical layer set the zone connects as a list of
    strings. When the zone only resides on one layer, the output of ``self.to_sexpr()`` will
    change into ``(layer "xyz")`` instead of ``(layers ..)`` automatically."""

    tstamp: Optional[str] = None       # Used since KiCad 6
    """The ``tstamp`` token defines the unique identifier of the zone object"""

    name: Optional[str] = None
    """The optional ``name`` token attribute defines the name of the zone if one has been assigned"""

    hatch: Hatch = field(default_factory=lambda: Hatch())
    """The ``hatch`` token attributes define the zone outline display hatch style and pitch"""

    priority: Optional[int] = None
    """The optional ``priority`` attribute defines the zone priority if it is not zero"""

    connectPads: Optional[str] = None  # This refers to CONNECTION_TYPE in the docu
    """The ``connectPads`` token attributes define the pad connection type and clearance. Valid
    pad connection types are ``thru_hole_only``, ``full`` and ``no``. If the pad connection type is not
    defined, thermal relief pad connections are used"""

    clearance: float = 0.254
    """The ``clearance`` token defines the thermal relief for pad connections. The usage of this
    token is depending on the value of ``connectPads``."""

    minThickness: float = 0.254
    """The ``minThickness`` token attributed defines the minimum fill width allowed in the zone"""

    filledAreasThickness: Optional[str] = None
    """The optional ``filledAreasThickness`` attribute no specifies if the zone like width is
    not used when determining the zone fill area. This is to maintain compatibility with older
    board files that included the line thickness when performing zone fills when it is not defined."""

    keepoutSettings: Optional[KeepoutSettings] = None
    """The optional ``keepoutSettings`` section defines the keep out items if the zone
    defines as a keep out area"""

    fillSettings: Optional[FillSettings] = None
    """The optional ``fillSettings`` section defines how the zone is to be filled"""

    polygons: List[ZonePolygon] = field(default_factory=list)
    """The ``polygon`` token defines a list of zone polygons that define the shape of the zone"""

    filledPolygons: List[FilledPolygon] = field(default_factory=list)
    """The ``filledPolygons`` token defines a list of filled polygons in the zone"""

    # TODO: This is KiCad 4 only stuff, needs to be tested yet ..
    fillSegments: Optional[FillSegments] = None
    """The optional ``fillSegments`` section defines a list of track segments used to fill
    the zone"""

    # Available since KiCad v9
    placement: Optional[PlacementSettings] = None

    attr_teardrop_type: Optional[AttrTeardrop] = None
    """The optional ``attr_teardrop_type`` token indicates if this is a teardrop zone and of which type"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Zone:
        """Convert the given S-Expresstion into a Zone object

        Args:
            - exp (list): Part of parsed S-Expression ``(zone ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not zone

        Returns:
            - Zone: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'zone':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, 'locked'): object.locked = parse_bool(item, 'locked')
            elif not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'net': object.net = int(item[1])
            elif item[0] == 'net_name': object.netName = item[1]
            elif item[0] == 'layers' or item[0] == 'layer':
                for layer in item[1:]:
                    object.layers.append(layer)
            elif item[0] == 'tstamp': object.tstamp = item[1]
            elif item[0] == 'uuid': object.tstamp = item[1] # Haha :)
            elif item[0] == 'name': object.name = item[1]
            elif item[0] == 'hatch': object.hatch = Hatch(style=item[1], pitch=item[2])
            elif item[0] == 'priority': object.priority = int(item[1])
            elif item[0] == 'connect_pads':
                if len(item) == 2:
                    object.clearance = item[1][1]
                else:
                    object.connectPads = item[1]
                    object.clearance = item[2][1]
            elif item[0] == 'min_thickness': object.minThickness = item[1]
            elif item[0] == 'filled_areas_thickness': object.filledAreasThickness = item[1]
            elif item[0] == 'keepout': object.keepoutSettings = KeepoutSettings().from_sexpr(item)
            elif item[0] == 'fill': object.fillSettings = FillSettings().from_sexpr(item)
            elif item[0] == 'polygon': object.polygons.append(ZonePolygon().from_sexpr(item))
            elif item[0] == 'filled_polygon': object.filledPolygons.append(FilledPolygon().from_sexpr(item))
            elif item[0] == 'fill_segments': object.fillSegments = FillSegments().from_sexpr(item)
            elif item[0] == 'placement': object.placement = PlacementSettings().from_sexpr(item)
            elif item[0] == 'attr': object.attr_teardrop_type = AttrTeardrop().from_sexpr(item)
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 2, newline: bool = True) -> str:
        """Generate the S-Expression representing this object.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 2.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Raises:
            - Exception: When the zone has no elements in its layer list

        Returns:
            - str: S-Expression of this object.
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        if len(self.layers) == 0:
            raise Exception("Zone: No layers set for this zone")

        layers_list = [escape_and_quote(layer) for layer in self.layers]
        if len(self.layers) == 1 and self.layers[0] != "F&B.Cu" and self.layers[0] != "*.Cu":
            layer_token = 'layer'
        else:
            layer_token = 'layers'

        expr = [
            'zone',
            ['net', self.net],
            ['net_name', escape_and_quote(self.netName)],
            format_bool('locked', self.locked),
            [layer_token] + layers_list,
        ]

        if self.tstamp is not None:
            expr.append(['uuid', quote(self.tstamp)])

        if self.name is not None:
            expr.append(['name', escape_and_quote(self.name)])

        expr.append(['hatch', self.hatch.style, self.hatch.pitch])

        if self.priority is not None:
            expr.append(['priority', self.priority])
        
        if self.attr_teardrop_type is not None:
            expr.append(self.attr_teardrop_type._to_sexpr_raw())

        connect_pads_expr = ['connect_pads']
        if self.connectPads is not None:
            connect_pads_expr.append(self.connectPads)
        connect_pads_expr.append(['clearance', self.clearance])
        expr.append(connect_pads_expr)

        expr.append(['min_thickness', float(self.minThickness)])

        if self.filledAreasThickness is not None:
            expr.append(['filled_areas_thickness', self.filledAreasThickness])

        if self.keepoutSettings is not None:
            expr.append(self.keepoutSettings._to_sexpr_raw())

        if self.placement is not None:
            expr.append(self.placement._to_sexpr_raw())

        if self.fillSettings is not None:
            expr.append(self.fillSettings._to_sexpr_raw())

        for polygon in self.polygons:
            expr.append(polygon._to_sexpr_raw())

        for polygon in self.filledPolygons:
            expr.append(polygon._to_sexpr_raw())

        if self.fillSegments is not None:
            expr.append(self.fillSegments._to_sexpr_raw())

        return expr


@dataclass
class PlacementSettings():

    enabled: bool = False

    sheet_name: str = ""

    @classmethod
    def from_sexpr(cls, exp: list) -> PlacementSettings:
        """Convert the given S-Expresstion into a PlacementSettings object

        Args:
            - exp (list): Part of parsed S-Expression ``(placement ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not placement

        Returns:
            - PlacementSettings: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'placement':
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(f"Expected list property [key, value], got: {item}. Full expression: {exp}")
            elif item[0] == 'enabled': object.enabled = parse_bool(item, 'enabled')
            elif item[0] == 'sheetname': object.sheet_name = item[1]
            else:
                raise ValueError(f"Unrecognized property key: {item[0]}. Full expression: {item}")

        return object

    def to_sexpr(self, indent: int = 0, newline: bool = False) -> str:
        """Generate the S-Expression representing this object. When no coordinates are set
        in the curve, the resulting S-Expression will be left empty.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to False.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        return [
            'placement',
            format_bool('enabled', self.enabled, yesno=True),
            ['sheetname', quote(self.sheet_name)],
        ]

@dataclass
class AttrTeardrop():
    """The ``attr_teardrop`` object defines the teardrop attributes of the zone"""

    class TeardropType(IntEnum):
        TD_NONE = 0 # Not a teardrop: just a standard zone
        TD_UNSPECIFIED = 1 # Not specified/unknown teardrop type
        TD_VIAPAD = 2 # a teardrop on a via or pad
        TD_TRACKEND = 3 # a teardrop on a track end
                        # (when 2 tracks having different widths have a teardrop on the
                        # end of the largest track)

    t_type: TeardropType = TeardropType.TD_NONE

    @classmethod
    def from_sexpr(cls, exp: list) -> AttrTeardrop:
        """Convert the given S-Expresstion into a AttrTeardrop object

        Args:
            - exp (list): Part of parsed S-Expression ``(attr (teardrop ...))``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not placement

        Returns:
            - AttrTeardrop: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != 'attr':
            raise Exception("Expression does not have the correct type")

        object = cls()
        teardrop_expr = exp[1]
        if teardrop_expr[0] != 'teardrop':
            raise Exception("Expression does not have the correct type, expecting: teardrop")

        type_expr = teardrop_expr[1]
        if type_expr[0] != 'type':
            raise Exception("Expression does not have the correct type, expecting: type")
        
        if type_expr[1] not in ['padvia', 'track_end']:
            raise Exception("Expression does not have the correct type, expecting: padvia or track_end")
        
        if type_expr[1] == 'padvia':
            object.t_type = cls.TeardropType.TD_VIAPAD
        elif type_expr[1] == 'track_end':
            object.t_type = cls.TeardropType.TD_TRACKEND

        return object

    def to_sexpr(self, indent: int = 0, newline: bool = False) -> str:
        """Generate the S-Expression representing this object. When no coordinates are set
        in the curve, the resulting S-Expression will be left empty.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to False.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        if self.t_type == self.TeardropType.TD_NONE:
            return []

        expr = ['attr']
        expr.append(['teardrop', ['type', 'padvia' if self.t_type == self.TeardropType.TD_VIAPAD else 'track_end']])

        return expr