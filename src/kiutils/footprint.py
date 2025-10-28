"""Classes to manage KiCad footprints

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0

Major changes:
    02.02.2022 - created

Documentation taken from:
    https://dev-docs.kicad.org/en/file-formats/sexpr-footprint/
"""

from __future__ import annotations

import calendar
import datetime
import re
from typing import Dict
from os import path

from kiutils.items.zones import Zone
from kiutils.items.brditems import Teardrops
from kiutils.items.common import Image, Coordinate, Net, Group, Font, EmbeddedFile
from kiutils.items.dimensions import Dimension
from kiutils.items.fpitems import *
from kiutils.items.gritems import *
from kiutils.utils.sexpr import sexp_prettify as prettify, sexp_to_string, parse_sexp
from kiutils.utils.string_utils import *
from kiutils.misc.config import *
from kiutils.utils.parsing_utils import *


@dataclass
class Attributes:
    """The ``attr`` token defines the list of attributes of a footprint.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_footprint_attributes
    """

    type: Optional[str] = None
    """The optional ``type`` token defines the type of footprint. Valid footprint types are ``smd`` and
    ``through_hole``. May be none when no attributes are set."""

    boardOnly: bool = False
    """The optional ``boardOnly`` token indicates that the footprint is only defined in the board
    and has no reference to any schematic symbol"""

    excludeFromPosFiles: bool = False
    """The optional ``excludeFromPosFiles`` token indicates that the footprint position information
    should not be included when creating position files"""

    excludeFromBom: bool = False
    """The optional ``excludeFromBom`` token indicates that the footprint should be excluded when
    creating bill of materials (BOM) files"""

    allowMissingCourtyard: bool = False
    """The optional ``allowMissingCourtyard`` token indicates if the footprint generates a 
    "missing courtyard" DRC violation.
    
    Available since KiCad 7"""

    # Available since KiCad v9

    dnp: Optional[bool] = None
    """The optional ``dnp`` token indicates that the footprint will not be populated"""

    allow_soldermask_bridges: Optional[bool] = None
    """The optional ``allow_soldermask_bridges`` token indicates that soldermask bridges are allowed"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Attributes:
        """Convert the given S-Expresstion into a Attributes object

        Args:
            - exp (list): Part of parsed S-Expression ``(attr ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not attr

        Returns:
            - Attributes: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "attr":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "board_only"):
                object.boardOnly = parse_bool(item, "board_only")
            elif is_bool_key(item, "exclude_from_pos_files"):
                object.excludeFromPosFiles = parse_bool(item, "exclude_from_pos_files")
            elif is_bool_key(item, "exclude_from_bom"):
                object.excludeFromBom = parse_bool(item, "exclude_from_bom")
            elif is_bool_key(item, "allow_missing_courtyard"):
                object.allowMissingCourtyard = parse_bool(
                    item, "allow_missing_courtyard"
                )
            elif is_bool_key(item, "dnp"):
                object.dnp = parse_bool(item, "dnp")
            elif is_bool_key(item, "allow_soldermask_bridges"):
                object.allow_soldermask_bridges = parse_bool(
                    item, "allow_soldermask_bridges"
                )
            elif item in ["through_hole", "smd"]:
                object.type = item
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

        return object

    def to_sexpr(self, indent=0, newline=False) -> str:
        """Generate the S-Expression representing this object. Will return an empty string, if the
        following attributes are selected:
        - ``type``: None
        - ``boardOnly``: False
        - ``excludeFromBom``: False
        - ``excludeFromPosFiles``: False
        - ``allowMissingCourtyard``: False
        - ``dnp``: None
        - ``allow_soldermask_bridges``: None

        KiCad won't add the ``(attr ..)`` token to a footprint when this combination is selected.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to False.

        Returns:
            - str: S-Expression of this object
        """
        if self.type is None and all(
            [
                prop == False
                for prop in [
                    self.boardOnly,
                    self.excludeFromBom,
                    self.excludeFromPosFiles,
                    self.allowMissingCourtyard,
                    self.dnp,
                    self.allow_soldermask_bridges,
                ]
            ]
        ):
            return ""

        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ["attr"]

        if self.type is not None:
            expr.append(self.type)
        if self.boardOnly:
            expr.append("board_only")
        if self.excludeFromPosFiles:
            expr.append("exclude_from_pos_files")
        if self.excludeFromBom:
            expr.append("exclude_from_bom")
        if self.allowMissingCourtyard:
            expr.append("allow_missing_courtyard")
        if self.dnp:
            expr.append("dnp")
        if self.allow_soldermask_bridges:
            expr.append("allow_soldermask_bridges")

        return expr


@dataclass
class Model:
    """The ``model`` token defines the 3D model associated with a footprint.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_footprint_3d_model
    """

    path: str = ""
    """The ``path`` attribute is the path and file name of the 3D model"""

    pos: Coordinate = field(default_factory=lambda: Coordinate(0.0, 0.0, 0.0))
    """The ``pos`` token specifies the 3D position coordinates of the model relative to the footprint"""

    scale: Coordinate = field(default_factory=lambda: Coordinate(1.0, 1.0, 1.0))
    """The ``scale`` token specifies the model scale factor for each 3D axis"""

    rotate: Coordinate = field(default_factory=lambda: Coordinate(0.0, 0.0, 0.0))
    """The ``rotate`` token specifies the model rotation for each 3D axis relative to the footprint"""

    hide: bool = False
    """The `hide` token specifies if the 3d model is visible or not"""

    opacity: Optional[float] = None
    """The optional opacity token specifies the opacity of the 3D model on a scale between 1.0 and 0.0."""

    @classmethod
    def from_sexpr(cls, exp: list) -> Model:
        """Convert the given S-Expresstion into a Model object

        Args:
            - exp (list): Part of parsed S-Expression ``(model ...)``

        Raises:
            - Exception: When given parameter's type is not a list or the list is not 5 long
            - Exception: When the first item of the list is not model

        Returns:
            - Model: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list) or len(exp) < 5:
            raise Exception("Expression does not have the correct type")

        if exp[0] != "model":
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.path = exp[1]

        for item in exp[2:]:
            if is_bool_key(item, "hide"):
                object.hide = parse_bool(item, "hide")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "opacity":
                object.opacity = item[1]
            elif item[0] == "offset":
                object.pos = Coordinate.from_sexpr(item[1])
            elif item[0] == "scale":
                object.scale = Coordinate.from_sexpr(item[1])
            elif item[0] == "rotate":
                object.rotate = Coordinate.from_sexpr(item[1])
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

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
        expr = ["model", escape_and_quote(self.path)]

        expr.append(format_bool("hide", self.hide))

        if self.opacity is not None:
            expr.append(["opacity", self.opacity])

        expr.append(["offset", self.pos._to_sexpr_raw()])
        expr.append(["scale", self.scale._to_sexpr_raw()])
        expr.append(["rotate", self.rotate._to_sexpr_raw()])

        return expr


@dataclass
class DrillDefinition:
    """The ``drill`` token defines the drill attributes for a footprint pad.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_pad_drill_definition
    """

    oval: bool = False
    """The ``oval`` token defines if the drill is oval instead of round"""

    diameter: Optional[float] = None
    """The ``diameter`` attribute defines the drill diameter"""

    width: Optional[float] = None
    """The optional ``width`` attribute defines the width of the slot for oval drills"""

    offset: Optional[Position] = None
    """The optional ``offset`` token defines the drill offset coordinates from the center of the pad"""

    @classmethod
    def from_sexpr(cls, exp: list) -> DrillDefinition:
        """Convert the given S-Expresstion into a DrillDefinition object

        Args:
            - exp (list): Part of parsed S-Expression ``(drill ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not drill

        Returns:
            - DrillDefinition: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "drill":
            raise Exception("Expression does not have the correct type")

        object = cls()

        for item in exp[1:]:
            if isinstance(item, str) and item == "oval":
                object.oval = True
            elif isinstance(item, (int, float, str)):
                num = float(item)
                if object.diameter is None:
                    object.diameter = object.width = num
                else:
                    object.width = num
            elif isinstance(item, list) and item[0] == "offset":
                object.offset = Position().from_sexpr(item)
            else:
                raise ValueError(
                    f"Expression does not have the correct type. Expected oval, size or offset, got: {item}"
                )

        return object

    def to_sexpr(self, indent: int = 0, newline: bool = False) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to False.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ["drill"]

        if self.oval:
            expr.append("oval")

        if self.diameter is not None:
            expr.append(self.diameter)

        if self.oval and self.width is not None:
            expr.append(self.width)

        if self.offset is not None:
            offset = ["offset", self.offset.X, self.offset.Y]
            expr.append(offset)

        return expr


@dataclass
class PadOptions:
    """The ``options`` token attributes define the settings used for custom pads. This token is
    only used when a custom pad is defined.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_custom_pad_options
    """

    clearance: str = "outline"
    """The ``clearance`` token defines the type of clearance used for a custom pad. Valid clearance
    types are ``outline`` and ``convexhull``."""

    anchor: str = "rect"
    """The ``anchor`` token defines the anchor pad shape of a custom pad. Valid anchor pad shapes
    are rect and circle."""

    @classmethod
    def from_sexpr(cls, exp: list) -> PadOptions:
        """Convert the given S-Expresstion into a PadOptions object

        Args:
            - exp (list): Part of parsed S-Expression ``(options ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not options

        Returns:
            - PadOptions: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "options":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "clearance":
                object.clearance = item[1]
            elif item[0] == "anchor":
                object.anchor = item[1]
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

        return object

    def to_sexpr(self, indent: int = 0, newline: bool = False) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to False.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        return ["options", ["clearance", self.clearance], ["anchor", self.anchor]]


@dataclass
class Pad:
    """The ``pad`` token defines a pad in a footprint definition.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_footprint_pad
    """

    number: str = "x"
    """The ``number`` attribute is the pad number"""

    type: str = "smd"
    """The pad ``type`` can be defined as ``thru_hole``, ``smd``, ``connect``, or ``np_thru_hole``"""

    shape: str = "rect"
    """The pad ``shape`` can be defined as ``circle``, ``rect``, ``oval``, ``trapezoid``, ``roundrect``, or
    ``custom``"""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` defines the X and Y coordinates and optional orientation angle of the pad"""

    locked: bool = False
    """The optional ``locked`` token defines if the footprint pad can be edited"""

    size: Position = field(
        default_factory=lambda: Position()
    )  # Size uses Position class for simplicity for now
    """The ``size`` token defines the width and height of the pad"""

    drill: Optional[DrillDefinition] = None
    """The optional pad ``drill`` token defines the pad drill requirements"""

    # TODO: Test case for one-layer pad??
    layers: List[str] = field(default_factory=list)
    """The ``layers`` token defines the layer or layers the pad reside on"""

    property: Optional[str] = None
    """The optional ``property`` token defines any special properties for the pad. Valid properties
    are ``pad_prop_bga``, ``pad_prop_fiducial_glob``, ``pad_prop_fiducial_loc``, ``pad_prop_testpoint``,
    ``pad_prop_heatsink``, ``pad_prop_heatsink``, and ``pad_prop_castellated``"""

    removeUnusedLayers: Optional[str] = None
    """The optional ``removeUnusedLayers`` token specifies that the copper should be removed from
    any layers the pad is not connected to"""

    keepEndLayers: Optional[str] = None
    """The optional ``keepEndLayers`` token specifies that the top and bottom layers should be
    retained when removing the copper from unused layers"""

    roundrectRatio: Optional[float] = None
    """The optional ``roundrectRatio`` token defines the scaling factor of the pad to corner radius
    for rounded rectangular and chamfered corner rectangular pads. The scaling factor is a
    number between 0 and 1."""

    chamferRatio: Optional[float] = None  # Adds a newline before
    """The optional ``chamferRatio`` token defines the scaling factor of the pad to chamfer size.
    The scaling factor is a number between 0 and 1."""

    chamfer: List[str] = field(default_factory=list)
    """The optional ``chamfer`` token defines a list of one or more rectangular pad corners that
    get chamfered. Valid chamfer corner attributes are ``top_left``, ``top_right``, ``bottom_left``,
    and ``bottom_right``."""

    net: Optional[Net] = None
    """The optional ``net`` token defines the integer number and name string of the net connection
    for the pad."""

    tstamp: Optional[str] = None  # Used since KiCad 6
    """The optional ``tstamp`` token defines the unique identifier of the pad object"""

    pinFunction: Optional[str] = None
    """The optional ``pinFunction`` token attribute defines the associated schematic symbol pin name"""

    pinType: Optional[str] = None
    """The optional ``pinType`` token attribute defines the associated schematic pin electrical type"""

    dieLength: Optional[float] = None  # Adds a newline before
    """The optional ``dieLength`` token attribute defines the die length between the component pad
    and physical chip inside the component package"""

    solderMaskMargin: Optional[float] = None
    """The optional ``solderMaskMargin`` token attribute defines the distance between the pad and
    the solder mask for the pad. If not set, the footprint solder_mask_margin is used."""

    solderPasteMargin: Optional[float] = None
    """The optional ``solderPasteMargin`` token attribute defines the distance the solder paste
    should be changed for the pad"""

    solderPasteMarginRatio: Optional[float] = None
    """The optional ``solderPasteMarginRatio`` token attribute defines the percentage to reduce the
    pad outline by to generate the solder paste size"""

    clearance: Optional[float] = None
    """The optional ``clearance`` token attribute defines the clearance from all copper to the pad.
    If not set, the footprint clearance is used."""

    zoneConnect: Optional[int] = None
    """The optional ``zoneConnect`` token attribute defines type of zone connect for the pad. If
    not defined, the footprint zone_connection setting is used. Valid connection types are
    integers values from 0 to 3 which defines:
    - 0: Pad is not connect to zone
    - 1: Pad is connected to zone using thermal relief
    - 2: Pad is connected to zone using solid fill
    - 3: Only through hold pad is connected to zone using thermal relief
    """

    thermalBridgeWidth: Optional[float] = None
    """The optional ``thermalBridgeWidth`` token attribute defines the thermal relief spoke width used for
    zone connection for the pad. This only affects a pad connected to a zone with a thermal
    relief. If not set, the footprint thermalBridgeWidth setting is used."""

    thermalBridgeAngle: Optional[float] = None
    """The optional ``thermalBridgeAngle`` affects angle of thermal relief spoke pad escape"""

    thermalGap: Optional[float] = None
    """The optional ``thermalGap`` token attribute defines the distance from the pad to the zone of
    the thermal relief connection for the pad. This only affects a pad connected to a zone
    with a thermal relief. If not set, the footprint thermal_gap setting is used."""

    customPadOptions: Optional[PadOptions] = None
    """The optional ``customPadOptions`` token defines the options when a custom pad is defined"""

    # Documentation seems wrong about primitives here. It seems like its just a list
    # of graphical objects, but the docu suggests, besides the list, two other params
    # for the primitive token: width and fill
    # These two however are note generated under the primitive token from the KiCad
    # generator. These two params may be found in gr_poly or gr_XX only.
    # So for now, the custom pad primitives are only a list of graphical objects
    customPadPrimitives: List = field(default_factory=list)
    """The optional ``customPadPrimitives`` defines the drawing objects and options used to define
    a custom pad"""

    # Available since KiCad v9

    zone_layer_connections: list[str] = field(default_factory=list)
    """The ``zone_layer_connections`` token indicates which copper layers are connected"""

    teardrops: Optional[Teardrops] = None
    """The optional ``teardrops`` token defines the teardrop connections for the pad"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Pad:
        """Convert the given S-Expresstion into a Pad object

        Args:
            - exp (list): Part of parsed S-Expression ``(pad ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not pad

        Returns:
            - Pad: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "pad":
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.number = exp[1]
        object.type = exp[2]
        object.shape = exp[3]

        for item in exp[4:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "at":
                object.position = Position().from_sexpr(item)
            elif item[0] == "size":
                object.size = Position().from_sexpr(item)
            elif item[0] == "drill":
                object.drill = DrillDefinition().from_sexpr(item)
            elif item[0] == "layers":
                object.layers.extend(item[1:])
            elif item[0] == "property":
                object.property = item[1]
            elif item[0] == "remove_unused_layers":
                object.removeUnusedLayers = item[1]
            elif item[0] == "keep_end_layers":
                object.keepEndLayers = item[1]
            elif item[0] == "roundrect_rratio":
                object.roundrectRatio = item[1]
            elif item[0] == "chamfer_ratio":
                object.chamferRatio = item[1]
            elif item[0] == "chamfer":
                object.chamfer.extend(item[1:])
            elif item[0] == "net":
                object.net = Net().from_sexpr(item)
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
            elif item[0] == "pinfunction":
                object.pinFunction = item[1]
            elif item[0] == "pintype":
                object.pinType = item[1]
            elif item[0] == "die_length":
                object.dieLength = item[1]
            elif item[0] == "solder_mask_margin":
                object.solderMaskMargin = item[1]
            elif item[0] == "solder_paste_margin":
                object.solderPasteMargin = item[1]
            elif item[0] in ["solder_paste_margin_ratio", "solder_paste_ratio"]:
                object.solderPasteMarginRatio = item[1]
            elif item[0] == "clearance":
                object.clearance = item[1]
            elif item[0] == "zone_connect":
                object.zoneConnect = item[1]
            elif item[0] in ["thermal_bridge_width", "thermal_width"]:
                object.thermalBridgeWidth = item[1]
            elif item[0] == "thermal_bridge_angle":
                object.thermalBridgeAngle = float(item[1])
            elif item[0] == "thermal_gap":
                object.thermalGap = item[1]
            elif item[0] == "options":
                object.customPadOptions = PadOptions().from_sexpr(item)
            elif item[0] == "primitives":
                for primitive in item[1:]:
                    if primitive[0] == "gr_text":
                        object.customPadPrimitives.append(
                            GrText().from_sexpr(primitive)
                        )
                    elif primitive[0] == "gr_text_box":
                        object.customPadPrimitives.append(
                            GrTextBox().from_sexpr(primitive)
                        )
                    elif primitive[0] == "gr_line":
                        object.customPadPrimitives.append(
                            GrLine().from_sexpr(primitive)
                        )
                    elif primitive[0] == "gr_rect":
                        object.customPadPrimitives.append(
                            GrRect().from_sexpr(primitive)
                        )
                    elif primitive[0] == "gr_circle":
                        object.customPadPrimitives.append(
                            GrCircle().from_sexpr(primitive)
                        )
                    elif primitive[0] == "gr_arc":
                        object.customPadPrimitives.append(GrArc().from_sexpr(primitive))
                    elif primitive[0] == "gr_poly":
                        object.customPadPrimitives.append(
                            GrPoly().from_sexpr(primitive)
                        )
                    elif primitive[0] == "gr_curve":
                        object.customPadPrimitives.append(
                            GrCurve().from_sexpr(primitive)
                        )
            elif item[0] == "zone_layer_connections":
                object.zone_layer_connections.extend(item[1:])
            elif item[0] == "teardrops":
                object.teardrops = Teardrops.from_sexpr(item)
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
        expr = ["pad", escape_and_quote(self.number), self.type, self.shape]

        expr.append(format_bool("locked", self.locked))

        pos = ["at", self.position.X, self.position.Y]
        if self.position.angle is not None:
            pos.append(self.position.angle)
        expr.append(pos)

        expr.append(["size", self.size.X, self.size.Y])

        if self.drill is not None:
            expr.append(self.drill._to_sexpr_raw())

        if self.property is not None:
            expr.append(["property", self.property])

        layers = ["layers"] + [escape_and_quote(layer) for layer in self.layers]
        expr.append(layers)

        if self.removeUnusedLayers is not None:
            expr.append(["remove_unused_layers", self.removeUnusedLayers])

        if self.keepEndLayers is not None:
            expr.append(["keep_end_layers", self.keepEndLayers])

        if len(self.zone_layer_connections) > 0:
            zlc_expr = ["zone_layer_connections"] + [
                escape_and_quote(layer) for layer in self.zone_layer_connections
            ]
            expr.append(zlc_expr)

        if self.roundrectRatio is not None:
            expr.append(["roundrect_rratio", self.roundrectRatio])

        if self.chamferRatio is not None:
            expr.append(["chamfer_ratio", self.chamferRatio])

        if len(self.chamfer) > 0:
            chamfer_expr = ["chamfer"] + self.chamfer
            expr.append(chamfer_expr)

        if self.dieLength is not None:
            expr.append(["die_length", self.dieLength])

        if self.net is not None:
            expr.append(self.net._to_sexpr_raw())

        if self.pinFunction is not None:
            expr.append(["pinfunction", escape_and_quote(self.pinFunction)])

        if self.pinType is not None:
            expr.append(["pintype", escape_and_quote(self.pinType)])

        if self.solderMaskMargin is not None:
            expr.append(["solder_mask_margin", self.solderMaskMargin])

        if self.solderPasteMargin is not None:
            expr.append(["solder_paste_margin", self.solderPasteMargin])

        if self.solderPasteMarginRatio is not None:
            expr.append(["solder_paste_margin_ratio", self.solderPasteMarginRatio])

        if self.clearance is not None:
            expr.append(["clearance", self.clearance])

        if self.zoneConnect is not None:
            expr.append(["zone_connect", self.zoneConnect])

        if self.thermalBridgeWidth is not None:
            expr.append(["thermal_bridge_width", self.thermalBridgeWidth])

        if self.thermalBridgeAngle is not None:
            expr.append(["thermal_bridge_angle", self.thermalBridgeAngle])

        if self.thermalGap is not None:
            expr.append(["thermal_gap", self.thermalGap])

        if self.customPadOptions is not None:
            expr.append(self.customPadOptions._to_sexpr_raw())

        if self.customPadPrimitives is not None and len(self.customPadPrimitives) > 0:
            primitives = ["primitives"]
            for primitive in self.customPadPrimitives:
                primitives.append(primitive._to_sexpr_raw())
            expr.append(primitives)

        if self.teardrops is not None:
            expr.append(self.teardrops._to_sexpr_raw())

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        return expr


@dataclass
class Footprint:
    """The ``footprint`` token defines a footprint.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_footprint
    """

    @property
    def libId(self) -> str:
        """The ``lib_id`` token defines the link to footprint library of the footprint.
        This only applies to footprints defined in the board file format, in a regular footprint
        file this id defines the footprint's name. In ``kiutils``, the token is a combination of
        both the ``libraryNickname`` and ``entryName`` token. Setting the ``lib_id`` token will
        update those tokens accordingly.

        Returns:
            - Symbol id in the following format: ``<libraryNickname>:<entryName>`` or ``<entryName>``,
              if ``libraryNickname`` token is not set.
        """
        if self.libraryNickname:
            return f"{self.libraryNickname}:{self.entryName}"
        else:
            return f"{self.entryName}"

    @libId.setter
    def libId(self, symbol_id: str):
        """Sets the ``lib_id`` token and parses its contents into the ``libraryNickname`` and
        ``entryName`` token.

        Args:
            - symbol_id (str): The symbol id in the following format: ``<libraryNickname>:<entryName>``
              or only ``<entryName>``
        """
        # kicad5 fix: module names may not be quoted strings (only numbers) - see PR #91
        parse_symbol_id = re.match(r"^(.+?):(.+?)$", str(symbol_id))
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

    version: Optional[str] = None
    """The ``version`` token attribute defines the symbol library version using the YYYYMMDD date format"""

    generator: Optional[str] = None
    """The ``generator`` token attribute defines the program used to write the file"""

    locked: bool = False
    """The optional ``locked`` token defines a flag to indicate the footprint cannot be edited"""

    placed: bool = False
    """The optional ``placed`` token defines a flag to indicate that the footprint has not been placed"""

    layer: str = "F.Cu"
    """The ``layer`` token defines the canonical layer the footprint is placed"""

    tedit: str = remove_prefix(
        hex(calendar.timegm(datetime.datetime.now().utctimetuple())), "0x"
    )
    """The ``tedit`` token defines a the last time the footprint was edited"""

    tstamp: Optional[str] = None
    """The ``tstamp`` token defines the unique identifier for the footprint. This only applies
    to footprints defined in the board file format."""

    position: Optional[Position] = None
    """The ``position`` token defines the X and Y coordinates and rotational angle of the
    footprint. This only applies to footprints defined in the board file format."""

    description: Optional[str] = None
    """The optional ``description`` token defines a string containing the description of the footprint"""

    tags: Optional[str] = None
    """The optional ``tags`` token defines a string of search tags for the footprint"""

    properties: Dict[str, FpProperty] = field(default_factory=dict)
    """The ``properties`` token defines dictionary of properties as key / value pairs where key being
    the name of the property and value being the description of the property, the FpProperty item"""

    path: Optional[str] = None
    """The ``path`` token defines the hierarchical path of the schematic symbol linked to the footprint.
    This only applies to footprints defined in the board file format."""

    autoplaceCost90: Optional[int] = None
    """The optional ``autoplaceCost90`` token defines the vertical cost of when using the automatic
    footprint placement tool. Valid values are integers 1 through 10. This only applies to footprints
    defined in the board file format."""

    autoplaceCost180: Optional[int] = None
    """The optional ``autoplaceCost180`` token defines the horizontal cost of when using the automatic
    footprint placement tool. Valid values are integers 1 through 10. This only applies to footprints
    defined in the board file format."""

    solderMaskMargin: Optional[float] = None
    """The optional ``solderMaskMargin`` token defines the solder mask distance from all pads in the
    footprint. If not set, the board solder_mask_margin setting is used."""

    solderPasteMargin: Optional[float] = None
    """The optional ``solderPasteMargin`` token defines the solder paste distance from all pads in
    the footprint. If not set, the board solder_paste_margin setting is used."""

    solderPasteMarginRatio: Optional[float] = None
    """The optional ``solderPasteMarginRatio`` token defines the ratio applied to the solder paste
    margin for all pads in the footprint. It scales the board's solder_paste_margin value by this ratio.
    If not set, the board ``solder_paste_margin_ratio`` setting is used."""

    solderPasteMarginRatio: Optional[float] = None
    """The optional ``solderPasteMarginRatio`` token defines the percentage of the pad size used to define
    the solder paste for all pads in the footprint. If not set, the board solder_paste_margin_ratio setting
    is used."""

    clearance: Optional[float] = None
    """The optional ``clearance`` token defines the clearance to all board copper objects for all pads
    in the footprint. If not set, the board clearance setting is used."""

    zoneConnect: Optional[int] = None
    """The optional ``zoneConnect`` token defines how all pads are connected to filled zone. If not
    defined, then the zone connect_pads setting is used. Valid connection types are integers values
    from 0 to 3 which defines:
      - 0: Pads are not connect to zone
      - 1: Pads are connected to zone using thermal reliefs
      - 2: Pads are connected to zone using solid fill
      - 3: Only through hold pads are connected to zone using thermal reliefs
    """

    thermalBridgeWidth: Optional[float] = None
    """The optional ``thermalBridgeWidth`` token defined the thermal relief spoke width used for zone connections
    for all pads in the footprint. This only affects pads connected to zones with thermal reliefs. If
    not set, the zone thermal_width setting is used."""

    thermalGap: Optional[float] = None
    """The optional ``thermalGap`` is the distance from the pad to the zone of thermal relief connections
    for all pads in the footprint. If not set, the zone thermal_gap setting is used. If not set, the
    zone thermal_gap setting is used."""

    attributes: Optional[Attributes] = None
    """The optional ``attributes`` section defines the attributes of the footprint"""

    privateLayers: List[str] = field(default_factory=list)
    """The optional ``privateLayers`` token defines a list of private layers assigned to the footprint.
    Valid values are: ``User.[1-9]``, ``User.Drawings``, ``User.Comments``, ``User.Eco[1-2]``.
    
    Available since KiCad v7."""

    netTiePadGroups: List[str] = field(default_factory=list)
    """The optional ``netTiePadGroups`` token defines a list of net tie groups assigned to the 
    footprint. 
    
    Available since KiCad v7."""

    # TODO: Type hinting for this list
    graphicItems: List = field(default_factory=list)
    """The ``graphic`` objects section is a list of one or more graphical objects in the footprint. 
    Possible items are defined in ``kiutils.items.fpitems``. At minimum the reference designator 
    and value text objects are defined. All other graphical objects are optional.

    The ``Image`` token is supported since KiCad v7 and must be added into this list when used."""

    pads: List[Pad] = field(default_factory=list)
    """The optional ``pads`` section is a list of pads in the footprint"""

    zones: List[Zone] = field(default_factory=list)
    """The optional ``zones`` section is a list of keep out zones in the footprint"""

    groups: List[Group] = field(default_factory=list)
    """The optional ``groups`` section is a list of grouped objects in the footprint"""

    models: List[Model] = field(default_factory=list)
    """The ``3D model`` section defines the 3D model object associated with the footprint"""

    filePath: Optional[str] = None
    """The ``filePath`` token defines the path-like string to the library file. Automatically set when
    ``self.from_file()`` is used. Allows the use of ``self.to_file()`` without parameters."""

    # Available since KiCad v9

    generator_version: Optional[str] = None
    """The ``generator_version`` token attribute defines the version of the program used to write the file"""

    embedded_fonts: Optional[bool] = None
    """The ``embedded_fonts`` token defines if the embedded fonts are used in the footprint"""

    sheet_name: str = ""
    """The ``sheet_name`` token defines name of the hierarchical sheet in which this footprint instance was placed."""

    sheet_file: str = ""
    """The ``sheet_file`` token defines filename of the schematic sheet file associated with this footprint instance."""

    embedded_files: list[EmbeddedFile] = field(default_factory=list)
    """The ``embedded_files`` store data of embedded files"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Footprint:
        """Convert the given S-Expresstion into a Footprint object

        Args:
            - exp (list): Part of parsed S-Expression ``(footprint ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not footprint

        Returns:
            - Footprint: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "module" and exp[0] != "footprint":
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.libId = exp[1]
        for item in exp[2:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif is_bool_key(item, "placed"):
                object.placed = parse_bool(item, "placed")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "version":
                object.version = item[1]
            elif item[0] == "generator":
                object.generator = item[1]
            elif item[0] == "generator_version":
                object.generator_version = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "tedit":
                object.tedit = item[1]
            elif item[0] == "descr":
                object.description = item[1]
            elif item[0] == "tags":
                object.tags = item[1]
            elif item[0] == "path":
                object.path = item[1]
            elif item[0] == "at":
                object.position = Position().from_sexpr(item)
            elif item[0] == "autoplace_cost90":
                object.autoplaceCost90 = item[1]
            elif item[0] == "autoplace_cost180":
                object.autoplaceCost180 = item[1]
            elif item[0] == "solder_mask_margin":
                object.solderMaskMargin = item[1]
            elif item[0] == "solder_paste_margin":
                object.solderPasteMargin = item[1]
            elif item[0] in ["solder_paste_margin_ratio", "solder_paste_ratio"]:
                object.solderPasteMarginRatio = item[1]
            elif item[0] == "clearance":
                object.clearance = item[1]
            elif item[0] == "zone_connect":
                object.zoneConnect = item[1]
            elif item[0] in ["thermal_bridge_width", "thermal_width"]:
                object.thermalBridgeWidth = item[1]
            elif item[0] == "thermal_gap":
                object.thermalGap = item[1]
            elif item[0] == "attr":
                object.attributes = Attributes.from_sexpr(item)
            elif item[0] == "model":
                object.models.append(Model.from_sexpr(item))
            elif item[0] == "fp_text":
                object.graphicItems.append(FpText.from_sexpr(item))
            elif item[0] == "fp_text_box":
                object.graphicItems.append(FpTextBox.from_sexpr(item))
            elif item[0] == "fp_line":
                object.graphicItems.append(FpLine.from_sexpr(item))
            elif item[0] == "fp_rect":
                object.graphicItems.append(FpRect.from_sexpr(item))
            elif item[0] == "fp_circle":
                object.graphicItems.append(FpCircle.from_sexpr(item))
            elif item[0] == "fp_arc":
                object.graphicItems.append(FpArc.from_sexpr(item))
            elif item[0] == "fp_poly":
                object.graphicItems.append(FpPoly.from_sexpr(item))
            elif item[0] == "fp_curve":
                object.graphicItems.append(FpCurve.from_sexpr(item))
            elif item[0] == "image":
                object.graphicItems.append(Image.from_sexpr(item))
            elif item[0] == "pad":
                object.pads.append(Pad.from_sexpr(item))
            elif item[0] == "zone":
                object.zones.append(Zone.from_sexpr(item))
            elif item[0] == "sheetname":
                object.sheet_name = item[1]
            elif item[0] == "sheetfile":
                object.sheet_file = item[1]
            elif item[0] == "property":
                object.properties.update({item[1]: FpProperty.from_sexpr(item)})
            elif item[0] == "group":
                object.groups.append(Group.from_sexpr(item))
            elif item[0] == "private_layers":
                object.privateLayers.extend(item[1:])
            elif item[0] == "net_tie_pad_groups":
                object.netTiePadGroups.extend(item[1:])
            elif item[0] == "dimension":
                object.graphicItems.append(Dimension.from_sexpr(item))
            elif item[0] == "embedded_fonts":
                object.embedded_fonts = parse_bool(item, "embedded_fonts")
            elif item[0] == "embedded_files":
                object.embedded_files.extend(
                    [EmbeddedFile().from_sexpr(f) for f in item[1:]]
                )
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

        return object

    @classmethod
    def from_file(cls, filepath: str, encoding: Optional[str] = None) -> Footprint:
        """Load a footprint directly from a KiCad footprint file (`.kicad_mod`) and sets the
        ``self.filePath`` attribute to the given file path.

        Args:
            - filepath (str): Path or path-like object that points to the file
            - encoding (str, optional): Encoding of the input file. Defaults to None (platform
                                        dependent encoding).

        Raises:
            - Exception: If the given path is not a file

        Returns:
            - Footprint: Object of the Footprint class initialized with the given KiCad footprint
        """
        if not path.isfile(filepath):
            raise Exception("Given path is not a file!")

        with open(filepath, "r", encoding=encoding) as infile:
            rawFootprint = infile.read()

            fpData = parse_sexp(rawFootprint)
            return cls.from_sexpr(fpData)

    @classmethod
    def create_new(
        cls, library_id: str, value: str, type: str = "other", reference: str = "REF**"
    ) -> Footprint:
        """Creates a new empty footprint with its attributes set as KiCad would create it

        Args:
            - library_link (str): Denotes the name of the library as well as the footprint. Like `Connector:Conn01x02`)
            - value (str): The value text item (printed on the fabrication layer as ``value`` attribute)
            - type (str): Type of footprint (``smd``, ``through_hole`` or ``other``). Defaults to 'other'.
            - reference (str): Reference of the footprint. Defaults to `REF**`.
        Raises:
            - Exception: When the given type is something other than listed above

        Returns:
            - Footprint: Empty footprint
        """
        if type not in ["smd", "through_hole", "other"]:
            raise Exception("Unsupported type was given")

        fp = Footprint()
        fp.version = KIUTILS_CREATE_NEW_VERSION_STR
        fp.generator = KIUTILS_CREATE_NEW_GENERATOR_STR
        fp.generator_version = KIUTILS_CREATE_NEW_GENERATOR_VERSION_STR
        fp.libId = library_id

        # Create text items that are created when adding a new footprint to a library
        fp.properties["Reference"] = (
            FpProperty(
                type="Reference",
                text=reference,
                layer="F.SilkS",
                effects=Effects(font=Font(thickness=0.15)),
                at=Position(X=0, Y=-0.5, unlocked=True),
            ),
        )
        fp.properties["Value"] = (
            FpProperty(
                type="Value",
                text=value,
                layer="F.Fab",
                effects=Effects(font=Font(thickness=0.15)),
                at=Position(X=0, Y=1, unlocked=True),
            ),
        )
        fp.graphicItems.append(
            FpText(
                type="user",
                text="${REFERENCE}",
                layer="F.Fab",
                effects=Effects(font=Font(thickness=0.15)),
                position=Position(X=0, Y=2.5, unlocked=True),
            )
        )

        # The type ``other`` does not set the attributes type token
        if type != "other":
            fp.attributes.type = type

        return fp

    def to_file(self, filepath=None, encoding: Optional[str] = None):
        """Save the object to a file in S-Expression format

        Args:
            - filepath (str, optional): Path-like string to the file. Defaults to None. If not set,
                                        the attribute ``self.filePath`` will be used instead.
            - encoding (str, optional): Encoding of the output file. Defaults to None (platform
                                        dependent encoding).

        Raises:
            - Exception: If no file path is given via the argument or via `self.filePath`
        """
        if filepath is None:
            if self.filePath is None:
                raise Exception("File path not set")
            filepath = self.filePath

        with open(filepath, "w", encoding=encoding) as outfile:
            pre_formatted_sexpr = self.to_sexpr()
            outfile.write(prettify(pre_formatted_sexpr))

    def to_sexpr(self, indent=0, newline=True, layerInFirstLine=False) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.
            - layerInFirstLine (bool): Prints the ``layer`` token in the first line. Defaults to False

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ["footprint", escape_and_quote(self.libId)]

        expr.append(format_bool("locked", self.locked))
        expr.append(format_bool("placed", self.placed))

        if self.version is not None:
            expr.append(["version", self.version])

        if self.generator is not None:
            expr.append(["generator", quote(self.generator)])

        if self.generator_version is not None:
            expr.append(["generator_version", quote(self.generator_version)])

        expr.append(["layer", escape_and_quote(self.layer)])

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        if self.position is not None:
            pos = ["at", self.position.X, self.position.Y]
            if self.position.angle is not None:
                pos.append(self.position.angle)
            expr.append(pos)

        if self.description is not None:
            expr.append(["descr", escape_and_quote(self.description)])

        if self.tags is not None:
            expr.append(["tags", escape_and_quote(self.tags)])

        for item in self.properties.values():
            expr.append(item._to_sexpr_raw())

        if self.path is not None:
            expr.append(["path", escape_and_quote(self.path)])

        if self.sheet_name != "":
            expr.append(["sheetname", escape_and_quote(self.sheet_name)])

        if self.sheet_file != "":
            expr.append(["sheetfile", escape_and_quote(self.sheet_file)])

        if self.autoplaceCost90 is not None:
            expr.append(["autoplace_cost90", self.autoplaceCost90])

        if self.autoplaceCost180 is not None:
            expr.append(["autoplace_cost180", self.autoplaceCost180])

        if self.solderMaskMargin is not None:
            expr.append(["solder_mask_margin", self.solderMaskMargin])

        if self.solderPasteMargin is not None:
            expr.append(["solder_paste_margin", self.solderPasteMargin])

        if self.solderPasteMarginRatio is not None:
            expr.append(["solder_paste_margin_ratio", self.solderPasteMarginRatio])

        if self.clearance is not None:
            expr.append(["clearance", self.clearance])

        if self.zoneConnect is not None:
            expr.append(["zone_connect", self.zoneConnect])

        if self.thermalBridgeWidth is not None:
            expr.append(["thermal_bridge_width", self.thermalBridgeWidth])

        if self.thermalGap is not None:
            expr.append(["thermal_gap", self.thermalGap])

        if self.attributes is not None:
            raw_attr = self.attributes._to_sexpr_raw()
            if raw_attr:  # only append if it's not empty
                expr.append(raw_attr)

        if self.privateLayers:
            private_layers = ["private_layers"] + [
                escape_and_quote(item) for item in self.privateLayers
            ]
            expr.append(private_layers)

        if self.netTiePadGroups:
            net_tie = ["net_tie_pad_groups"] + [
                escape_and_quote(item) for item in self.netTiePadGroups
            ]
            expr.append(net_tie)

        for item in self.graphicItems:
            expr.append(item._to_sexpr_raw())

        for item in self.pads:
            expr.append(item._to_sexpr_raw())

        for item in self.zones:
            expr.append(item._to_sexpr_raw())

        for item in self.groups:
            expr.append(item._to_sexpr_raw())

        if self.embedded_fonts is not None:
            expr.append(format_bool("embedded_fonts", self.embedded_fonts, yesno=True))

        # Embedded files
        if len(self.embedded_files) > 0:
            embedded_files_expr = ["embedded_files"] + [
                f._to_sexpr_raw() for f in self.embedded_files
            ]
            expr.append(embedded_files_expr)

        for item in self.models:
            expr.append(item._to_sexpr_raw())

        return expr
