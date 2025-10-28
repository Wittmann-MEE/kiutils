"""Classes to manage KiCad board items

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0

Major changes:
    20.02.2022 - created

Documentation taken from:
    https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List

from kiutils.items.common import Position
from kiutils.utils.string_utils import *
from kiutils.utils.parsing_utils import *
from kiutils.utils.sexpr import sexp_to_string


@dataclass
class GeneralSettings:
    """The ``general`` token define general information about the board

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/#_general_section
    """

    thickness: float = 1.6
    """The ``thickness`` token attribute defines the overall board thickness"""

    # Available since KiCad v9

    legacy_teardrops: str = "no"

    @classmethod
    def from_sexpr(cls, exp: list) -> GeneralSettings:
        """Convert the given S-Expresstion into a GeneralSettings object

        Args:
            - exp (list): Part of parsed S-Expression ``(general ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not general

        Returns:
            - GeneralSettings: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "general":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "thickness":
                object.thickness = item[1]
            elif item[0] == "legacy_teardrops":
                object.legacy_teardrops = item[1]
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
        expr = ["general", ["thickness", self.thickness]]

        if self.legacy_teardrops is not None:
            expr.append(["legacy_teardrops", self.legacy_teardrops])

        return expr


@dataclass
class LayerToken:
    """Intermediate type used for the ``layers`` token in a board

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/#_layers_section
    """

    ordinal: int = 0
    """The layer ``ordinal`` is an integer used to associate the layer stack ordering. This is mostly
    to ensure correct mapping when the number of layers is increased in the future"""

    name: str = "F.Cu"
    """The ``name`` is the layer name defined for internal board use"""

    type: str = "signal"
    """The layer ``type`` defines the type of layer and can be defined as ``jumper``, ``mixed``, ``power``,
    ``signal``, or ``user``."""

    userName: Optional[str] = None
    """The optional ``userName`` attribute defines the custom user name"""

    @classmethod
    def from_sexpr(cls, exp: list) -> LayerToken:
        """Convert the given S-Expresstion into a LayerToken object

        Args:
            - exp (list): Part of parsed S-Expression ``(<nr> "<name>" <type>)``

        Raises:
            - Exception: When given parameter's type is not a list or the length of the list is not 3 - 4
            - Exception: When the first item of the list is not kicad_pcb

        Returns:
            - LayerToken: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list) or len(exp) < 3 or len(exp) > 4:
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.ordinal = exp[0]
        object.name = exp[1]
        object.type = exp[2]
        if len(exp) == 4:
            object.userName = exp[3]

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
        expr = [self.ordinal, escape_and_quote(self.name), self.type]

        if self.userName is not None:
            expr.append(escape_and_quote(self.userName))

        return expr


@dataclass
class StackupSubLayer:
    """The ``StackupSubLayer`` token defines a sublayer used when stacking dielectrics in a PCB"""

    thickness: float = 0.1
    """The ``thickness`` token defines the thickness of the sublayer. Defaults to 0.1"""

    material: Optional[str] = None
    """The optional ``material`` token defines a string that describes the sublayer material"""

    epsilonR: Optional[float] = None
    """The optional ``epsilonR`` token defines the dielectric constant of the sublayer material"""

    lossTangent: Optional[float] = None
    """The optional layer ``lossTangent`` token defines the dielectric loss tangent of the sublayer"""

    @classmethod
    def from_sexpr(cls, exp: list) -> StackupSubLayer:
        """This class cannot be derived from an S-Expression as the format currently used in KiCad
        board files does not match the usual convention. Assign member values manually when using
        this object.

        Raises:
            - NotImplementedError"""
        raise NotImplementedError("This class cannot be derived from an S-Expression!")

    def to_sexpr(self, indent=0, newline=False) -> str:
        """Generate the S-Expression representing this object. The representation differs from the
        normal form of an S-Expression as this uses no opening and closing parenthesis.

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to False.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = ["addsublayer", ["thickness", self.thickness]]

        if self.material is not None:
            expr.append(["material", self.material])

        if self.epsilonR is not None:
            expr.append(["epsilon_r", self.epsilonR])

        if self.lossTangent is not None:
            expr.append(["loss_tangent", self.lossTangent])

        return expr


@dataclass
class StackupLayer:
    """The ``layer`` token defines the stack up setting of a single layer in the board stack up
    settings.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/#_stack_up_settings
    """

    name: str = ""
    """The ``name`` attribute is either one of the canonical copper or technical layer names
    or ``dielectric ID`` if it is dielectric layer"""

    # Not found in example project ...
    # number: int = 0
    """The ``number`` attribute defines the stack order of the layer"""

    type: str = ""
    """The ``type`` token defines a string that describes the layer"""

    color: Optional[str] = None
    """The optional ``color`` token defines a string that describes the layer color. This is
    only used on solder mask and silkscreen layers"""

    thickness: Optional[float] = None
    """The optional ``thickness`` token defines the thickness of the layer where appropriate"""

    material: Optional[str] = None
    """The optional ``material`` token defines a string that describes the layer material
    where appropriate"""

    epsilonR: Optional[float] = None
    """The optional ``epsilonR`` token defines the dielectric constant of the layer material"""

    lossTangent: Optional[float] = None
    """The optional layer ``lossTangent`` token defines the dielectric loss tangent of the layer"""

    subLayers: List[StackupSubLayer] = field(default_factory=list)
    """The ``sublayers`` token defines a list of zero or more sublayers that are used to create
    stacks of dielectric layers. Does not apply to copper-type layers."""

    @classmethod
    def from_sexpr(cls, exp: list) -> StackupLayer:
        """Convert the given S-Expresstion into a StackupLayer object

        Args:
            - exp (list): Part of parsed S-Expression ``(layer ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not layer

        Returns:
            - StackupLayer: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "layer":
            raise Exception("Expression does not have the correct type")

        parsingSublayer = False
        tempSublayer = StackupSubLayer()
        object = cls()
        object.name = exp[1]
        for item in exp[2:]:
            if not isinstance(item, list):
                # Start parsing the layer's sublayer if the first sublayer token was found
                if item == "addsublayer":
                    if parsingSublayer:
                        # When the ``addsublayer`` token was found a second time, the previously
                        # parsed sublayer will be appended to the list of sublayers
                        object.subLayers.append(tempSublayer)
                        tempSublayer = StackupSubLayer()
                    else:
                        # Change state of the parser to look for StackupSubLayer tokens
                        parsingSublayer = True
                continue

            # Parse the tokens of StackupSubLayer for the current sublayer
            if parsingSublayer:
                if item[0] == "thickness":
                    tempSublayer.thickness = item[1]
                if item[0] == "material":
                    tempSublayer.material = item[1]
                if item[0] == "epsilon_r":
                    tempSublayer.epsilonR = item[1]
                if item[0] == "loss_tangent":
                    tempSublayer.lossTangent = item[1]
                continue

            # Parse the normal tokens of StackupLayer token
            if item[0] == "type":
                object.type = item[1]
            if item[0] == "thickness":
                object.thickness = item[1]
            if item[0] == "material":
                object.material = item[1]
            if item[0] == "epsilon_r":
                object.epsilonR = item[1]
            if item[0] == "loss_tangent":
                object.lossTangent = item[1]
            if item[0] == "color":
                object.color = item[1]

        # Add the last parsed sublayer to the list, if any
        if parsingSublayer:
            object.subLayers.append(tempSublayer)

        return object

    def to_sexpr(self, indent=6, newline=True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 6.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = [
            "layer",
            escape_and_quote(self.name),
            ["type", escape_and_quote(self.type)],
        ]

        if self.color is not None:
            expr.append(["color", escape_and_quote(self.color)])

        if self.thickness is not None:
            expr.append(["thickness", self.thickness])

        if self.material is not None:
            expr.append(["material", escape_and_quote(self.material)])

        if self.epsilonR is not None:
            expr.append(["epsilon_r", self.epsilonR])

        if self.lossTangent is not None:
            expr.append(["loss_tangent", self.lossTangent])

        for layer in self.subLayers:
            expr.append(layer._to_sexpr_raw())

        return expr


@dataclass
class Stackup:
    """The ``stackup`` token defines the board stack up settings and is defined in the setup
    section.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/#_stack_up_settings
    """

    layers: List[StackupLayer] = field(default_factory=list)
    """The ``layers``token is a list of layer settings for each layer required to manufacture
    a board including the dielectric material between the actual layers defined in the board
    editor."""

    copperFinish: Optional[str] = None
    """The optional ``copperFinish`` token is a string that defines the copper finish used to
    manufacture the board"""

    dielectricContraints: Optional[str] = None
    """The optional ``dielectricContraints`` token define if the board should meet all
    dielectric requirements. Valid values are ``yes`` and ``no``."""

    edgeConnector: Optional[str] = None
    """The optional ``edgeConnector`` token defines if the board has an edge connector
    (value: ``yes``) and if the edge connector is bevelled (value: ``bevelled``)"""

    castellatedPads: bool = False
    """The ``castellatedPads`` token defines if the board edges contain castellated pads"""

    edgePlating: bool = False
    """The ``edgePlating`` token defines if the board edges should be plated."""

    @classmethod
    def from_sexpr(cls, exp: list) -> Stackup:
        """Convert the given S-Expresstion into a Stackup object

        Args:
            - exp (list): Part of parsed S-Expression ``(stackup ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not stackup

        Returns:
            - Stackup: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "stackup":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "castellated_pads"):
                object.castellatedPads = parse_bool(item, "castellated_pads")
            elif is_bool_key(item, "edge_plating"):
                object.edgePlating = parse_bool(item, "edge_plating")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "layer":
                object.layers.append(StackupLayer().from_sexpr(item))
            elif item[0] == "copper_finish":
                object.copperFinish = item[1]
            elif item[0] == "dielectric_constraints":
                object.dielectricContraints = item[1]
            elif item[0] == "edge_connector":
                object.edgeConnector = item[1]
            else:
                raise ValueError("Unrecognized property key: {item[0]}")

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
        expr = ["stackup"]

        for layer in self.layers:
            expr.append(layer._to_sexpr_raw())

        if self.copperFinish is not None:
            expr.append(["copper_finish", escape_and_quote(self.copperFinish)])

        if self.dielectricContraints is not None:
            expr.append(["dielectric_constraints", self.dielectricContraints])

        if self.edgeConnector is not None:
            expr.append(["edge_connector", self.edgeConnector])

        if self.castellatedPads:
            expr.append(format_bool("castellated_pads", self.castellatedPads))

        if self.edgePlating:
            expr.append(format_bool("edge_plating", self.edgePlating))

        return expr


@dataclass
class PlotSettings:
    """The ``pcbplotparams`` token defines the plotting and printing settings used for the last
    plot and is defined in the set up section.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/#_plot_settings
    """

    layerSelection: str = ""
    """The ``layerSelection`` token defines a hexadecimal bit set of the layers to plot"""

    plotOnAllLayersSelection: Optional[str] = None
    """The ``plotOnAllLayersSelection`` token defines a hexadecimal bit set of layers where all 
    selected layers shall be plotted.
    
    Available and required since KiCad v7"""

    disableApertMacros: Optional[bool] = None
    """The optional ``disableApertMacros`` token defines if aperture macros are to be used in gerber plots"""

    useGerberExtensions: Optional[bool] = None
    """The optional ``useGerberExtensions`` token defines if the Protel layer file name extensions are to
    be used in gerber plots"""

    useGerberAttributes: Optional[bool] = None
    """The optional ``useGerberAttributes`` token defines if the X2 extensions are used in gerber plots"""

    useGerberAdvancedAttributes: Optional[bool] = None
    """The optional ``useGerberAdvancedAttributes`` token defines if the netlist information should be
    included in gerber plots"""

    createGerberJobFile: Optional[bool] = None
    """The optional ``createGerberJobFile`` token defines if a job file should be created when plotting 
    gerber files"""

    # FIXME: Where is the docu of this token?
    dashedLineDashRatio: Optional[float] = None
    """The ``dashedLineDashRatio`` token's documentation is still missing ..
    
    Available and required since KiCad v7"""

    # FIXME: Where is the docu of this token?
    dashedLineGapRatio: Optional[float] = None
    """The ``dashedLineGapRatio`` token's documentation is still missing ..
    
    Available and required since KiCad v7"""

    svgUseInch: Optional[str] = None
    """The ``svgUseInch`` token defines if inch units should be use when plotting SVG files.
    
    Required until KiCad v6, removed since KiCad v7"""

    svgPrecision: float = 0.0
    """The ``svgPrecision`` token defines the units precision used when plotting SVG files"""

    excludeEdgeLayer: Optional[str] = None
    """The ``excludeEdgeLayer`` token defines if the board edge layer is plotted on all layers.
    
    Required until KiCad v6, removed since KiCad v7"""

    plotFameRef: Optional[bool] = None
    """The optional ``plotFameRef`` token defines if the border and title block should be plotted"""

    viasOnMask: Optional[bool] = None
    """The optional ``viasOnMask`` token defines if the vias are to be tented"""

    mode: int = 1
    """The ``mode`` token defines the plot mode. An attribute of 1 plots in the normal
    mode and an attribute of 2 plots in the outline (sketch) mode."""

    useAuxOrigin: Optional[bool] = None
    """The optional ``useAuxOrigin`` token determines if all coordinates are offset by the defined user origin"""

    hpglPenNumber: int = 0
    """The ``hpglPenNumber`` token defines the integer pen number used for HPGL plots"""

    hpglPenSpeed: int = 0
    """The ``hpglPenSpeed`` token defines the integer pen speed used for HPGL plots"""

    hpglPenDiameter: float = 0.0
    """The ``hpglPenDiameter`` token defines the floating point pen size for HPGL plots"""

    dxfPolygonMode: Optional[bool] = None
    """The optional ``dxfPolygonMode`` token defines if the polygon mode should be used for DXF plots"""

    dxfImperialUnits: Optional[bool] = None
    """The optional ``dxfImperialUnits`` token defines if imperial units should be used for DXF plots"""

    dxfUsePcbnewFont: Optional[bool] = None
    """The optional ``dxfUsePcbnewFont`` token defines if the Pcbnew font (vector font) or the default
    font should be used for DXF plots"""

    psNegative: Optional[bool] = None
    """The optional ``psNegative`` token defines if the output should be the negative for PostScript plots"""

    psA4Output: Optional[bool] = None
    """The optional ``psA4Output`` token defines if the A4 page size should be used for PostScript plots"""

    plotReference: Optional[bool] = None
    """The optional ``plotReference`` token defines if hidden reference field text should be plotted"""

    plotValue: Optional[bool] = None
    """The optional ``plotValue`` token defines if hidden value field text should be plotted"""

    plotInvisibleText: Optional[bool] = None
    """The optional ``plotInvisibleText`` token defines if hidden text other than the reference and
    value fields should be plotted"""

    sketchPadsOnFab: Optional[bool] = None
    """The optional ``sketchPadsOnFab`` token defines if pads should be plotted in the outline (sketch) mode"""

    subtractMaskFromSilk: Optional[bool] = None
    """The optional ``subtractMaskFromSilk`` token defines if the solder mask layers should be subtracted from
    the silk screen layers for gerber plots"""

    outputFormat: int = 0
    """The ``outputFormat`` token defines the last plot type. The following values are defined:
    - 0: gerber
    - 1: PostScript
    - 2: SVG
    - 3: DXF
    - 4: HPGL
    - 5: PDF"""

    mirror: Optional[bool] = None
    """The optional ``mirror`` token defines if the plot should be mirrored"""

    drillShape: int = 0
    """The ``drillShape`` token defines the type of drill marks used for drill files"""

    scaleSelection: int = 1
    """The ``scaleSelection`` is not documented yet (as of 20.02.2022)"""

    outputDirectory: str = ""
    """The ``drillShape`` token defines the path relative to the current project path
    where the plot files will be saved"""

    # Available since KiCad v9

    pdf_front_fp_property_popups: Optional[bool] = None
    """The optional ``pdf_front_fp_property_popups`` token defines if interactive popups for
    front-side footprint properties are included in PDF output"""

    pdf_back_fp_property_popups: Optional[bool] = None
    """The optional ``pdf_back_fp_property_popups`` token defines if interactive popups for
    back-side footprint properties are included in PDF output"""

    pdf_metadata: Optional[bool] = None
    """The optional ``pdf_metadata`` token defines if document metadata should be embedded
    in the PDF output"""

    pdf_single_document: Optional[bool] = None
    """The optional ``pdf_single_document`` token defines if all layers should be plotted
    into a single PDF document"""

    plot_black_and_white: Optional[bool] = None
    """The optional ``plot_black_and_white`` token defines if the plot should be generated
    in black and white"""

    hide_dnp_on_fab: Optional[bool] = None
    """The optional ``hide_dnp_on_fab`` token defines if 'Do Not Populate' footprints should
    be hidden on fabrication plots"""

    crossout_dnp_on_fab: Optional[bool] = None
    """The optional ``crossout_dnp_on_fab`` token defines if 'Do Not Populate' footprints
    should be crossed out on fabrication plots"""

    sketch_dnp_on_fab: Optional[bool] = None
    """The optional ``sketch_dnp_on_fab`` token defines if 'Do Not Populate' footprints should
    be drawn in sketch mode on fabrication plots"""

    plot_pad_numbers: Optional[bool] = None
    """The optional ``plot_pad_numbers`` token defines if pad numbers should be plotted
    on fabrication layers"""

    plot_fp_text: Optional[bool] = None
    """The optional ``plot_fp_text`` token defines if footprint text should be plotted
    on fabrication layers"""

    @classmethod
    def from_sexpr(cls, exp: list) -> PlotSettings:
        """Convert the given S-Expresstion into a PlotSettings object

        Args:
            - exp (list): Part of parsed S-Expression ``(pcbplotparams ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not pcbplotparams

        Returns:
            - PlotSettings: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "pcbplotparams":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "layerselection":
                object.layerSelection = item[1]
            elif item[0] == "plot_on_all_layers_selection":
                object.plotOnAllLayersSelection = item[1]
            elif item[0] == "disableapertmacros":
                object.disableApertMacros = item[1]
            elif item[0] == "usegerberextensions":
                object.useGerberExtensions = item[1]
            elif item[0] == "usegerberattributes":
                object.useGerberAttributes = item[1]
            elif item[0] == "usegerberadvancedattributes":
                object.useGerberAdvancedAttributes = item[1]
            elif item[0] == "creategerberjobfile":
                object.createGerberJobFile = item[1]
            elif item[0] == "dashed_line_dash_ratio":
                object.dashedLineDashRatio = item[1]
            elif item[0] == "dashed_line_gap_ratio":
                object.dashedLineGapRatio = item[1]
            elif item[0] == "svguseinch":
                object.svgUseInch = item[1]
            elif item[0] == "svgprecision":
                object.svgPrecision = item[1]
            elif item[0] == "excludeedgelayer":
                object.excludeEdgeLayer = item[1]
            elif item[0] == "plotframeref":
                object.plotFameRef = parse_bool(item, "plotframeref")
            elif item[0] == "viasonmask":
                object.viasOnMask = parse_bool(item, "viasonmask")
            elif item[0] == "mode":
                object.mode = item[1]
            elif item[0] == "useauxorigin":
                object.useAuxOrigin = parse_bool(item, "useauxorigin")
            elif item[0] == "hpglpennumber":
                object.hpglPenNumber = item[1]
            elif item[0] == "hpglpenspeed":
                object.hpglPenSpeed = item[1]
            elif item[0] == "hpglpendiameter":
                object.hpglPenDiameter = item[1]
            elif item[0] == "dxfpolygonmode":
                object.dxfPolygonMode = parse_bool(item, "dxfpolygonmode")
            elif item[0] == "dxfimperialunits":
                object.dxfImperialUnits = parse_bool(item, "dxfimperialunits")
            elif item[0] == "dxfusepcbnewfont":
                object.dxfUsePcbnewFont = parse_bool(item, "dxfusepcbnewfont")
            elif item[0] == "psnegative":
                object.psNegative = parse_bool(item, "psnegative")
            elif item[0] == "psa4output":
                object.psA4Output = parse_bool(item, "psa4output")
            elif item[0] == "plotreference":
                object.plotReference = parse_bool(item, "plotreference")
            elif item[0] == "plotvalue":
                object.plotValue = parse_bool(item, "plotvalue")
            elif item[0] == "plotinvisibletext":
                object.plotInvisibleText = parse_bool(item, "plotinvisibletext")
            elif item[0] == "sketchpadsonfab":
                object.sketchPadsOnFab = parse_bool(item, "sketchpadsonfab")
            elif item[0] == "subtractmaskfromsilk":
                object.subtractMaskFromSilk = parse_bool(item, "subtractmaskfromsilk")
            elif item[0] == "outputformat":
                object.outputFormat = item[1]
            elif item[0] == "mirror":
                object.mirror = parse_bool(item, "mirror")
            elif item[0] == "drillshape":
                object.drillShape = item[1]
            elif item[0] == "scaleselection":
                object.scaleSelection = item[1]
            elif item[0] == "outputdirectory":
                object.outputDirectory = item[1]
            elif item[0] == "pdf_front_fp_property_popups":
                object.pdf_front_fp_property_popups = parse_bool(
                    item, "pdf_front_fp_property_popups"
                )
            elif item[0] == "pdf_back_fp_property_popups":
                object.pdf_back_fp_property_popups = parse_bool(
                    item, "pdf_back_fp_property_popups"
                )
            elif item[0] == "pdf_metadata":
                object.pdf_metadata = parse_bool(item, "pdf_metadata")
            elif item[0] == "pdf_single_document":
                object.pdf_single_document = parse_bool(item, "pdf_single_document")
            elif item[0] == "plot_black_and_white":
                object.plot_black_and_white = parse_bool(item, "plot_black_and_white")
            elif item[0] == "hidednponfab":
                object.hide_dnp_on_fab = parse_bool(item, "hidednponfab")
            elif item[0] == "sketchdnponfab":
                object.sketch_dnp_on_fab = parse_bool(item, "sketchdnponfab")
            elif item[0] == "crossoutdnponfab":
                object.crossout_dnp_on_fab = parse_bool(item, "crossoutdnponfab")
            elif item[0] == "plotpadnumbers":
                object.plot_pad_numbers = parse_bool(item, "plotpadnumbers")
            elif item[0] == "plotfptext":
                object.plot_fp_text = parse_bool(item, "plotfptext")
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

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
        expr = ["pcbplotparams", ["layerselection", self.layerSelection]]

        if self.plotOnAllLayersSelection is not None:
            expr.append(["plot_on_all_layers_selection", self.plotOnAllLayersSelection])

        expr.append(["disableapertmacros", self.disableApertMacros])
        expr.append(["usegerberextensions", self.useGerberExtensions])
        expr.append(["usegerberattributes", self.useGerberAttributes])
        expr.append(["usegerberadvancedattributes", self.useGerberAdvancedAttributes])
        expr.append(["creategerberjobfile", self.createGerberJobFile])

        if self.dashedLineDashRatio is not None:
            expr.append(["dashed_line_dash_ratio", (f"{self.dashedLineDashRatio:.6f}")])

        if self.dashedLineGapRatio is not None:
            expr.append(["dashed_line_gap_ratio", (f"{self.dashedLineGapRatio:.6f}")])

        if self.svgUseInch is not None:
            expr.append(["svguseinch", self.svgUseInch])

        expr.append(["svgprecision", self.svgPrecision])

        if self.excludeEdgeLayer is not None:
            expr.append(["excludeedgelayer", self.excludeEdgeLayer])

        if self.plotFameRef is not None:
            expr.append(format_bool("plotframeref", self.plotFameRef, yesno=True))

        if self.viasOnMask is not None:
            expr.append(format_bool("viasonmask", self.viasOnMask, yesno=True))

        expr.append(["mode", self.mode])

        if self.useAuxOrigin is not None:
            expr.append(format_bool("useauxorigin", self.useAuxOrigin, yesno=True))

        expr.append(["hpglpennumber", self.hpglPenNumber])
        expr.append(["hpglpenspeed", self.hpglPenSpeed])
        expr.append(["hpglpendiameter", (f"{self.hpglPenDiameter:.6f}")])

        if self.pdf_front_fp_property_popups is not None:
            expr.append(
                format_bool(
                    "pdf_front_fp_property_popups",
                    self.pdf_front_fp_property_popups,
                    yesno=True,
                )
            )

        if self.pdf_back_fp_property_popups is not None:
            expr.append(
                format_bool(
                    "pdf_back_fp_property_popups",
                    self.pdf_back_fp_property_popups,
                    yesno=True,
                )
            )

        if self.pdf_metadata is not None:
            expr.append(format_bool("pdf_metadata", self.pdf_metadata, yesno=True))

        if self.pdf_single_document is not None:
            expr.append(
                format_bool("pdf_single_document", self.pdf_single_document, yesno=True)
            )

        if self.dxfPolygonMode is not None:
            expr.append(format_bool("dxfpolygonmode", self.dxfPolygonMode, yesno=True))

        if self.dxfImperialUnits is not None:
            expr.append(
                format_bool("dxfimperialunits", self.dxfImperialUnits, yesno=True)
            )

        if self.dxfUsePcbnewFont is not None:
            expr.append(
                format_bool("dxfusepcbnewfont", self.dxfUsePcbnewFont, yesno=True)
            )

        if self.psNegative is not None:
            expr.append(format_bool("psnegative", self.psNegative, yesno=True))

        if self.psA4Output is not None:
            expr.append(format_bool("psa4output", self.psA4Output, yesno=True))

        if self.plotReference is not None:
            expr.append(format_bool("plotreference", self.plotReference, yesno=True))

        if self.plotValue is not None:
            expr.append(format_bool("plotvalue", self.plotValue, yesno=True))

        if self.plot_black_and_white is not None:
            expr.append(
                format_bool(
                    "plot_black_and_white", self.plot_black_and_white, yesno=True
                )
            )

        if self.plot_fp_text is not None:
            expr.append(format_bool("plotfptext", self.plot_fp_text, yesno=True))

        if self.plotInvisibleText is not None:
            expr.append(
                format_bool("plotinvisibletext", self.plotInvisibleText, yesno=True)
            )

        if self.sketchPadsOnFab is not None:
            expr.append(
                format_bool("sketchpadsonfab", self.sketchPadsOnFab, yesno=True)
            )

        if self.plot_pad_numbers is not None:
            expr.append(
                format_bool("plotpadnumbers", self.plot_pad_numbers, yesno=True)
            )

        if self.hide_dnp_on_fab is not None:
            expr.append(format_bool("hidednponfab", self.hide_dnp_on_fab, yesno=True))

        if self.sketch_dnp_on_fab is not None:
            expr.append(
                format_bool("sketchdnponfab", self.sketch_dnp_on_fab, yesno=True)
            )

        if self.crossout_dnp_on_fab is not None:
            expr.append(
                format_bool("crossoutdnponfab", self.crossout_dnp_on_fab, yesno=True)
            )

        if self.subtractMaskFromSilk is not None:
            expr.append(
                format_bool(
                    "subtractmaskfromsilk", self.subtractMaskFromSilk, yesno=True
                )
            )

        expr.append(["outputformat", self.outputFormat])

        if self.mirror is not None:
            expr.append(format_bool("mirror", self.mirror, yesno=True))

        expr.append(["drillshape", self.drillShape])
        expr.append(["scaleselection", self.scaleSelection])
        expr.append(["outputdirectory", escape_and_quote(self.outputDirectory)])

        return expr


@dataclass
class SetupData:
    """The setup token is used to store the current settings such as default item sizes and
    other options used by the board

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/#_setup_section
    """

    stackup: Optional[Stackup] = None
    """The optional ``stackup`` define the parameters required to manufacture the board"""

    packToMaskClearance: float = 0.0
    """The ``packToMaskClearance`` token defines the clearance between footprint pads and
    the solder mask"""

    solderMaskMinWidth: Optional[float] = None
    """The optional ``solderMaskMinWidth`` defines the minimum solder mask width. If not
    defined, the minimum width is zero."""

    padToPasteClearance: Optional[float] = None
    """The optional ``padToPasteClearance`` defines the clearance between footprint pads
    and the solder paste layer. If not defined, the clearance is zero"""

    padToPasteClearanceRatio: Optional[float] = None
    """The optional ``padToPasteClearanceRatio`` is the percentage (from 0 to 100) of the
    footprint pad to make the solder paste. If not defined, the ratio is 100% (the same
    size as the pad)."""

    auxAxisOrigin: Optional[Position] = None
    """The optional ``auxAxisOrigin`` defines the auxiliary origin if it is set to anything
    other than (0,0)."""

    gridOrigin: Optional[Position] = None
    """The optional ``gridOrigin`` defines the grid original if it is set to anything other
    than (0,0)."""

    plotSettings: Optional[PlotSettings] = None
    """The optional ``plotSettings`` define how the board was last plotted."""

    # Available since KiCad v9

    allow_soldermask_bridges_in_footprints: Optional[bool] = None
    """The optional ``allow_soldermask_bridges_in_footprints`` defines if soldermask bridges
    in footprints are allowed."""

    tenting: List[str] = field(default_factory=list)
    """The ``tenting`` token defines which features are tented (covered by mask)"""

    covering: List[str] = field(default_factory=list)
    """The ``covering`` token defines which features are covered (e.g., hole covered)"""

    plugging: List[str] = field(default_factory=list)
    """The ``plugging`` token defines which features are plugged (filled with epoxy/resin)"""

    capping: List[str] = field(default_factory=list)
    """The ``capping`` token defines which features are capped (metal/finish over a filled/plugged via)"""

    filling: List[str] = field(default_factory=list)
    """The ``filling`` token defines which features are filled (completely filled bore)"""

    @classmethod
    def from_sexpr(cls, exp: list) -> SetupData:
        """Convert the given S-Expresstion into a SetupData object

        Args:
            - exp (list): Part of parsed S-Expression ``(setup ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not setup

        Returns:
            - SetupData: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "setup":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "stackup":
                object.stackup = Stackup().from_sexpr(item)
            elif item[0] == "pcbplotparams":
                object.plotSettings = PlotSettings().from_sexpr(item)
            elif item[0] == "pad_to_mask_clearance":
                object.packToMaskClearance = item[1]
            elif item[0] == "solder_mask_min_width":
                object.solderMaskMinWidth = item[1]
            elif item[0] == "pad_to_paste_clearance":
                object.padToPasteClearance = item[1]
            elif item[0] == "pad_to_paste_clearance_ratio":
                object.padToPasteClearanceRatio = item[1]
            elif item[0] == "aux_axis_origin":
                object.auxAxisOrigin = Position().from_sexpr(item)
            elif item[0] == "grid_origin":
                object.gridOrigin = Position().from_sexpr(item)
            elif item[0] == "pcbplotparams":
                object.plotSettings = PlotSettings().from_sexpr(item)
            elif item[0] == "allow_soldermask_bridges_in_footprints":
                object.allow_soldermask_bridges_in_footprints = parse_bool(
                    item, "allow_soldermask_bridges_in_footprints"
                )
            elif item[0] == "tenting":
                object.tenting.extend(item[1:])
            elif item[0] == "covering":
                object.covering.extend(item[1:])
            elif item[0] == "plugging":
                object.plugging.extend(item[1:])
            elif item[0] == "capping":
                object.capping.extend(item[1:])
            elif item[0] == "filling":
                object.filling.extend(item[1:])
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
        expr = ["setup"]

        if self.stackup is not None:
            expr.append(self.stackup._to_sexpr_raw())

        expr.append(["pad_to_mask_clearance", self.packToMaskClearance])

        if self.solderMaskMinWidth is not None:
            expr.append(["solder_mask_min_width", self.solderMaskMinWidth])

        if self.padToPasteClearance is not None:
            expr.append(["pad_to_paste_clearance", self.padToPasteClearance])

        if self.padToPasteClearanceRatio is not None:
            expr.append(["pad_to_paste_clearance_ratio", self.padToPasteClearanceRatio])

        if self.allow_soldermask_bridges_in_footprints is not None:
            expr.append(
                format_bool(
                    "allow_soldermask_bridges_in_footprints",
                    self.allow_soldermask_bridges_in_footprints,
                    yesno=True,
                )
            )

        if len(self.tenting) > 0:
            expr.append(["tenting"] + self.tenting)

        if self.auxAxisOrigin is not None:
            expr.append(["aux_axis_origin", self.auxAxisOrigin.X, self.auxAxisOrigin.Y])

        if self.gridOrigin is not None:
            expr.append(["grid_origin", self.gridOrigin.X, self.gridOrigin.Y])

        if len(self.covering) > 0:
            expr.append(["covering"] + self.covering)

        if len(self.plugging) > 0:
            expr.append(["plugging"] + self.plugging)

        if len(self.capping) > 0:
            expr.append(["capping"] + self.capping)

        if len(self.filling) > 0:
            expr.append(["filling"] + self.filling)

        if self.plotSettings is not None:
            expr.append(self.plotSettings._to_sexpr_raw())

        return expr


@dataclass
class Segment:
    """The ``segment`` token defines a track segment in a KiCad board

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/#_track_segment
    """

    start: Position = field(default_factory=lambda: Position())
    """The ``start`` token defines the coordinates of the beginning of the line"""

    end: Position = field(default_factory=lambda: Position())
    """The ``end`` token defines the coordinates of the end of the line"""

    width: float = 0.1
    """The ``width`` token defines the line width"""

    layer: str = "F.Cu"
    """The ``layer`` token defines the canonical layer the track segment resides on"""

    locked: bool = False
    """The ``locked`` token defines if the line cannot be edited"""

    net: int = 0
    """The ``net`` token defines by the net ordinal number which net in the net
    section that the segment is part of"""

    tstamp: str = ""
    """The ``tstamp`` token defines the unique identifier of the line object"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Segment:
        """Convert the given S-Expresstion into a Segment object

        Args:
            - exp (list): Part of parsed S-Expression ``(segment ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not segment

        Returns:
            - Segment: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "segment":
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
                object.start = Position().from_sexpr(item)
            elif item[0] == "end":
                object.end = Position().from_sexpr(item)
            elif item[0] == "width":
                object.width = item[1]
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "net":
                object.net = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
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
        expr = [
            "segment",
            ["start", self.start.X, self.start.Y],
            ["end", self.end.X, self.end.Y],
            ["width", self.width],
        ]

        if self.locked:
            expr.append(format_bool("locked", self.locked))

        expr.extend(
            [
                ["layer", escape_and_quote(self.layer)],
                ["net", self.net],
                ["uuid", quote(self.tstamp)],
            ]
        )

        return expr


@dataclass
class Via:
    """The ``via`` token defines a track via in a KiCad board

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/#_track_via
    """

    type: Optional[str] = None
    """The optional ``type`` attribute specifies the via type. Valid via types are ``blind`` and
    ``micro``. If no type is defined, the via is a through hole type"""

    locked: bool = False
    """The ``locked`` token defines if the line cannot be edited"""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` token define the coordinates of the center of the via"""

    size: float = 0.0
    """The ``size`` token define the diameter of the via annular ring"""

    drill: float = 0.0
    """The ``drill`` token define the drill diameter of the via"""

    layers: List[str] = field(default_factory=list)
    """The ``layers`` token define the canonical layer set the via connects as a list
    of strings"""

    removeUnusedLayers: bool = False
    """The ``removeUnusedLayers`` token is undocumented (as of 20.02.2022)"""

    keepEndLayers: bool = False
    """The ``keepEndLayers`` token is undocumented (as of 20.02.2022)"""

    free: bool = False
    """The ``free`` token indicates that the via is free to be moved outside it's assigned net"""

    net: int = 0
    """The ``net`` token defines by net ordinal number which net in the net section that
    the via is part of"""

    tstamp: Optional[str] = None
    """The ``tstamp`` token defines the unique identifier of the via"""

    # Available since KiCad v9

    zone_layer_connections: list[str] = field(default_factory=list)
    """The ``zone_layer_connections`` token indicates which copper layers are connected"""

    teardrops: Optional[Teardrops] = None
    """The optional ``teardrops`` token defines the teardrop connections for the pad"""

    tenting: List[str] = field(default_factory=list)
    """The ``tenting`` token defines which features are tented (covered by mask)"""

    covering: List[str] = field(default_factory=list)
    """The ``covering`` token defines which features are covered (e.g., hole covered)"""

    plugging: List[str] = field(default_factory=list)
    """The ``plugging`` token defines which features are plugged (filled with epoxy/resin)"""

    capping: List[str] = field(default_factory=list)
    """The ``capping`` token defines which features are capped (metal/finish over a filled/plugged via)"""

    filling: List[str] = field(default_factory=list)
    """The ``filling`` token defines which features are filled (completely filled bore)"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Via:
        """Convert the given S-Expresstion into a Via object

        Args:
            - exp (list): Part of parsed S-Expression ``(via ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not via

        Returns:
            - Via: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "via":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif is_bool_key(item, "remove_unused_layers"):
                object.removeUnusedLayers = parse_bool(item, "remove_unused_layers")
            elif is_bool_key(item, "keep_end_layers"):
                object.keepEndLayers = parse_bool(item, "keep_end_layers")
            elif is_bool_key(item, "free"):
                object.free = parse_bool(item, "free")
            elif not isinstance(item, list) and item in ["micro", "blind"]:
                object.type = item
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "at":
                object.position = Position().from_sexpr(item)
            elif item[0] == "size":
                object.size = item[1]
            elif item[0] == "drill":
                object.drill = item[1]
            elif item[0] == "layers":
                object.layers.extend(item[1:])
            elif item[0] == "net":
                object.net = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
            elif item[0] == "zone_layer_connections":
                object.zone_layer_connections.extend(item[1:])
            elif item[0] == "teardrops":
                object.teardrops = Teardrops.from_sexpr(item)
            elif item[0] == "tenting":
                object.tenting.extend(item[1:])
            elif item[0] == "covering":
                object.covering.extend(item[1:])
            elif item[0] == "plugging":
                object.plugging.extend(item[1:])
            elif item[0] == "capping":
                object.capping.extend(item[1:])
            elif item[0] == "filling":
                object.filling.extend(item[1:])
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
        expr = ["via"]

        if self.type is not None:
            expr.append(self.type)

        expr.extend(
            [
                ["at", self.position.X, self.position.Y],
                ["size", self.size],
                ["drill", self.drill],
            ]
        )

        layer_list = ["layers"]
        for layer in self.layers:
            layer_list.append(escape_and_quote(layer))
        expr.append(layer_list)

        if self.removeUnusedLayers:
            expr.append(format_bool("remove_unused_layers", self.removeUnusedLayers))

        if self.keepEndLayers:
            expr.append(format_bool("keep_end_layers", self.keepEndLayers))

        if self.locked:
            expr.append(format_bool("locked", self.locked))

        if self.free:
            expr.append(format_bool("free", self.free))

        if len(self.zone_layer_connections) > 0:
            expr.append(
                ["zone_layer_connections"]
                + [escape_and_quote(layer) for layer in self.zone_layer_connections]
            )

        if len(self.tenting) > 0:
            expr.append(["tenting"] + self.tenting)

        if len(self.covering) > 0:
            expr.append(["covering"] + self.covering)

        if len(self.plugging) > 0:
            expr.append(["plugging"] + self.plugging)

        if len(self.capping) > 0:
            expr.append(["capping"] + self.capping)

        if len(self.filling) > 0:
            expr.append(["filling"] + self.filling)

        if self.teardrops is not None:
            expr.append(self.teardrops._to_sexpr_raw())

        if self.zone_layer_connections:
            expr.append(["zone_layer_connections"])

        expr.append(["net", self.net])

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        return expr


@dataclass
class Arc:
    """The ``arc`` token defines a track arc, which will be generated when using the length-matching
    feature on differential pairs.

    Documentation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/#_track_arc
    """

    start: Position = field(default_factory=lambda: Position())
    """The ``start`` token defines the coordinates of the beginning of the arc"""

    mid: Position = field(default_factory=lambda: Position())
    """The ``mid`` token defines the coordinates of the mid point of the radius of the arc"""

    end: Position = field(default_factory=lambda: Position())
    """The ``end`` token defines the coordinates of the end of the arc"""

    width: float = 0.2
    """The ``width`` token defines the line width of the arc. Defaults to 0,2."""

    layer: str = "F.Cu"
    """The ``layer`` token defiens the canonical layer the track arc resides on. Defaults to `F.Cu`."""

    locked: bool = False
    """The ``locked`` token defines if the arc cannot be edited. Defaults to False."""

    net: int = 0
    """The ``net`` token defines the net ordinal number which net in the net section that arc is part
    of. Defaults to 0."""

    tstamp: Optional[str] = None
    """The optional ``tstamp`` token defines the unique identifier of the arc"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Arc:
        """Convert the given S-Expresstion into a Arc object

        Args:
            - exp (list): Part of parsed S-Expression ``(arc ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not ``arc``

        Returns:
            - Arc: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "arc":
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
                object.start = Position().from_sexpr(item)
            elif item[0] == "mid":
                object.mid = Position().from_sexpr(item)
            elif item[0] == "end":
                object.end = Position().from_sexpr(item)
            elif item[0] == "width":
                object.width = item[1]
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "net":
                object.net = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
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

    def _to_sexpr_raw(self, zone_poly=False):
        expr = ["arc"]

        if self.locked:
            expr.append(format_bool("locked", self.locked))

        expr.extend(
            [
                ["start", self.start.X, self.start.Y],
                ["mid", self.mid.X, self.mid.Y],
                ["end", self.end.X, self.end.Y],
            ]
        )

        if not zone_poly:
            expr.extend(
                [
                    ["width", self.width],
                    ["layer", escape_and_quote(self.layer)],
                    ["net", self.net],
                ]
            )

        if self.tstamp is not None:
            expr.append(["uuid", quote(self.tstamp)])

        return expr


@dataclass
class Target:
    """The ``target`` token defines a target marker on the PCB

    Documentation:
        Not found in KiCad docu - 15.06.2022
    """

    type: str = "plus"
    """The ``type`` token specifies the shape of the marker. Valid types are ``plus`` and ``x``."""

    position: Position = field(default_factory=lambda: Position())
    """The ``position`` token specifies the position of the target marker"""

    size: float = 0
    """The ``size`` token sets the marker's size"""

    width: float = 0.1
    """The ``width`` token sets the marker's line width"""

    layer: str = "F.Cu"
    """The ``layer`` token sets the canonical layer where the target marker resides"""

    tstamp: Optional[str] = None
    """The ``tstamp`` token defines the unique identifier of the target"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Target:
        """Convert the given S-Expresstion into a Target object

        Args:
            - exp (list): Part of parsed S-Expression ``(target ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not target

        Returns:
            - Target: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "target":
            raise Exception("Expression does not have the correct type")

        object = cls()
        object.type = exp[1]
        for item in exp[2:]:
            if not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "at":
                object.position = Position().from_sexpr(item)
            elif item[0] == "size":
                object.size = item[1]
            elif item[0] == "width":
                object.width = item[1]
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "tstamp":
                object.tstamp = item[1]
            elif item[0] == "uuid":
                object.tstamp = item[1]  # Haha :)
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
        return [
            "target",
            self.type,
            ["at", self.position.X, self.position.Y],
            ["size", self.size],
            ["width", self.width],
            ["layer", quote(self.layer)],
            ["uuid", quote(self.tstamp)],
        ]


@dataclass
class Generated:
    """The ``generated`` token defines an editable trace tuning object

    Documentation:
        https://docs.kicad.org/8.0/en/pcbnew/pcbnew.html#length-tuning
    """

    uuid: str = ""
    """The ``uuid`` defines the universally unique identifier"""

    type: str = ""
    """The ``type`` token defines the type of the tuned track """

    name: str = ""
    """The ``name`` token defines the name of the tuned track"""

    layer: str = "F.Cu"
    """The ``layer`` token defines the canonical layer the tuned track resides on"""

    locked: Optional[bool] = None
    """The ``locked`` token defines if the object can be edited"""

    base_line: list[Position] = field(default_factory=list)
    """The ``base_line`` token defines a primary line that tuned tracks are alligned to"""

    base_line_coupled: list[Position] = field(default_factory=list)
    """The ``base_line_coupled`` token defines the coupled base line of the tuned tracks"""

    corner_radius: int = 0
    """The ``corner_radius`` token defines the radius of the corner"""

    end: Position = field(default_factory=lambda: Position())
    """The ``end`` token defines the end of the tuned track"""

    initial_side: str = ""
    """The ``initial_side`` token defines the initial side of the tuned track"""

    last_diff_pair_gap: float = 0.0
    """The ``last_diff_pair_gap`` token holds the value of the last used differential pair gap"""

    last_net_name: str = ""
    """The ``last_net_name`` token holds the last used net name"""

    last_status: str = ""
    """The ``last_status`` token holds the last status of the tuned track"""

    last_track_width: float = 0.0
    """The ``last_track_width`` token holds the last width of the tuned track"""

    last_tuning: str = ""
    """The ``last_tuning`` token holds the last tuning of the tuned track"""

    max_amplitude: float = 0.0
    """The ``max_amplitude`` token defines the maximal amplitude of the tuned track"""

    min_amplitude: float = 0.0
    """The ``min_amplitude`` token defines the minimal amplitude of the tuned track"""

    min_spacing: float = 0.0
    """The ``min_spacing`` token defines the minimal spacing of the tuned track"""

    origin: Position = field(default_factory=lambda: Position())
    """The ``origin`` token defines the origin of the tuned track"""

    override_custom_rules: str = ""
    """The ``override_custom_rules`` token enables to bypass the custom rules"""

    rounded: str = ""
    """The ``rounded`` token defines if the tuned track is rounded"""

    single_sided: str = ""
    """The ``single_sided`` token defines if the tuned track is single sided"""

    target_length: float = 0.0
    """The ``target_length`` token defines the target length of the tuned track"""

    target_length_max: float = 0.0
    """The ``target_length_max`` token defines the maximal length of the tuned track"""

    target_length_min: float = 0.0
    """The ``target_length_min`` token defines the minimal length of the tuned track"""

    target_skew: float = 0.0
    """The ``target_skew`` token defines the target skew of the tuned track"""

    target_skew_max: float = 0.0
    """The ``target_skew_max`` token defines the maximal target skew of the tuned track"""

    target_skew_min: float = 0.0
    """The ``target_skew_min`` token defines the minimal target skew of the tuned track"""

    tuning_mode: str = ""
    """The ``tuningMode`` token defines the mode of tuning the tuned track"""

    members: list[str] = field(default_factory=list)
    """The ``members`` token defines the members of the tuned track"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Generated:
        """Convert the given S-Expresstion into a Generated object

        Args:
            - exp (list): Part of parsed S-Expression ``(generated ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not generator

        Returns:
            - Generated: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "generated":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "locked"):
                object.locked = parse_bool(item, "locked")
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "uuid":
                object.uuid = item[1]
            elif item[0] == "type":
                object.type = item[1]
            elif item[0] == "name":
                object.name = item[1]
            elif item[0] == "layer":
                object.layer = item[1]
            elif item[0] == "base_line":
                points_expr = item[1]
                if points_expr[0] != "pts":
                    raise Exception(f"Expected points property pts, got: {points_expr}")
                for point in points_expr[1:]:
                    object.base_line.append(Position().from_sexpr(point))
            elif item[0] == "base_line_coupled":
                points_expr = item[1]
                if points_expr[0] != "pts":
                    raise Exception(f"Expected points property pts, got: {points_expr}")
                for point in points_expr[1:]:
                    object.base_line_coupled.append(Position().from_sexpr(point))
            elif item[0] == "corner_radius_percent":
                object.corner_radius = item[1]
            elif item[0] == "end":
                object.end = Position().from_sexpr(item[1])
            elif item[0] == "initial_side":
                object.initial_side = item[1]
            elif item[0] == "last_diff_pair_gap":
                object.last_diff_pair_gap = item[1]
            elif item[0] == "last_netname":
                object.last_net_name = item[1]
            elif item[0] == "last_status":
                object.last_status = item[1]
            elif item[0] == "last_track_width":
                object.last_track_width = item[1]
            elif item[0] == "last_tuning":
                object.last_tuning = item[1]
            elif item[0] == "max_amplitude":
                object.max_amplitude = item[1]
            elif item[0] == "min_amplitude":
                object.min_amplitude = item[1]
            elif item[0] == "min_spacing":
                object.min_spacing = item[1]
            elif item[0] == "origin":
                object.origin = Position().from_sexpr(item[1])
            elif item[0] == "override_custom_rules":
                object.override_custom_rules = item[1]
            elif item[0] == "rounded":
                object.rounded = item[1]
            elif item[0] == "single_sided":
                object.single_sided = item[1]
            elif item[0] == "target_length":
                object.target_length = item[1]
            elif item[0] == "target_length_max":
                object.target_length_max = item[1]
            elif item[0] == "target_length_min":
                object.target_length_min = item[1]
            elif item[0] == "target_skew":
                object.target_skew = item[1]
            elif item[0] == "target_skew_max":
                object.target_skew_max = item[1]
            elif item[0] == "target_skew_min":
                object.target_skew_min = item[1]
            elif item[0] == "tuning_mode":
                object.tuning_mode = item[1]
            elif item[0] == "members":
                for member in item[1:]:
                    object.members.append(member)
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
        expr = [
            "generated",
            ["uuid", escape_and_quote(self.uuid)],
            ["type", self.type],
            ["name", escape_and_quote(self.name)],
            ["layer", escape_and_quote(self.layer)],
        ]

        if self.locked:
            expr.append(format_bool("locked", self.locked))

        if len(self.base_line) > 0:
            base_line_pts = ["pts"]
            for point in self.base_line:
                base_line_pts.append(["xy", point.X, point.Y])
            expr.append(["base_line", base_line_pts])

        if len(self.base_line_coupled) > 0:
            coupled_pts = ["pts"]
            for point in self.base_line_coupled:
                coupled_pts.append(["xy", point.X, point.Y])
            expr.append(["base_line_coupled", coupled_pts])

        expr.append(["corner_radius_percent", self.corner_radius])
        expr.append(["end", ["xy", self.end.X, self.end.Y]])
        expr.append(["initial_side", escape_and_quote(self.initial_side)])
        expr.append(["last_diff_pair_gap", self.last_diff_pair_gap])
        expr.append(["last_netname", escape_and_quote(self.last_net_name)])
        expr.append(["last_status", escape_and_quote(self.last_status)])
        expr.append(["last_track_width", self.last_track_width])
        expr.append(["last_tuning", escape_and_quote(self.last_tuning)])
        expr.append(["max_amplitude", self.max_amplitude])
        expr.append(["min_amplitude", self.min_amplitude])
        expr.append(["min_spacing", self.min_spacing])
        expr.append(["origin", ["xy", self.origin.X, self.origin.Y]])
        expr.append(["override_custom_rules", self.override_custom_rules])
        expr.append(["rounded", self.rounded])
        expr.append(["single_sided", self.single_sided])
        expr.append(["target_length", self.target_length])
        expr.append(["target_length_max", self.target_length_max])
        expr.append(["target_length_min", self.target_length_min])
        expr.append(["target_skew", self.target_skew])
        expr.append(["target_skew_max", self.target_skew_max])
        expr.append(["target_skew_min", self.target_skew_min])
        expr.append(["tuning_mode", escape_and_quote(self.tuning_mode)])

        if len(self.members) > 0:
            members = ["members"] + [quote(member) for member in self.members]
            expr.append(members)

        return expr


@dataclass
class Teardrops:
    """The ``teardrops`` object defines the via/pad teardrop connections"""

    max_length: Optional[float] = None
    """The optional ``max_length`` token defines the maximum length of the teardrop"""

    max_width: Optional[float] = None
    """The optional ``max_width`` token defines the maximum width of the teardrop"""

    best_length_ratio: Optional[float] = None
    """The optional ``best_length_ratio`` token defines the length of teardrop in relation the pad/via size"""

    best_width_ratio: Optional[float] = None
    """The optional ``best_width_ratio`` token defines the width (on wider side) of teardrop in relation the pad/via size"""

    filter_ratio: Optional[float] = None
    """The optional ``filter_ratio`` token defines the ratio of the teardrop width to the pad/via size"""

    curved_edges: Optional[bool] = None
    """The optional ``curved_edges`` token defines if the teardrop has curved edges"""

    enabled: Optional[bool] = None
    """The optional ``enabled`` token defines if the teardrop should be generated"""

    allow_two_segments: Optional[bool] = None
    """The optional ``allow_two_segments`` token defines if the teardrop can span over two segments"""

    prefer_zone_connections: Optional[bool] = None
    """The optional ``prefer_zone_connections`` token defines if zone connections should use teardrops"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Teardrops:
        """Convert the given S-Expresstion into a Teardrops object

        Args:
            - exp (list): Part of parsed S-Expression ``(teardrops ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not generator

        Returns:
            - Teardrops: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "teardrops":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if is_bool_key(item, "enabled"):
                object.enabled = parse_bool(item, "enabled")
            elif is_bool_key(item, "curved_edges"):
                object.curved_edges = parse_bool(item, "curved_edges")
            elif is_bool_key(item, "allow_two_segments"):
                object.allow_two_segments = parse_bool(item, "allow_two_segments")
            elif is_bool_key(item, "prefer_zone_connections"):
                object.prefer_zone_connections = parse_bool(
                    item, "prefer_zone_connections"
                )
            elif not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "max_length":
                object.max_length = float(item[1])
            elif item[0] == "max_width":
                object.max_width = float(item[1])
            elif item[0] == "best_length_ratio":
                object.best_length_ratio = float(item[1])
            elif item[0] == "best_width_ratio":
                object.best_width_ratio = float(item[1])
            elif item[0] == "filter_ratio":
                object.filter_ratio = float(item[1])
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
        expr = ["teardrops"]

        field_specs = {
            "best_length_ratio": lambda v: ["best_length_ratio", v],
            "max_length": lambda v: ["max_length", v],
            "best_width_ratio": lambda v: ["best_width_ratio", v],
            "max_width": lambda v: ["max_width", v],
            "curved_edges": lambda v: format_bool("curved_edges", v, yesno=True),
            "filter_ratio": lambda v: ["filter_ratio", v],
            "enabled": lambda v: format_bool("enabled", v, yesno=True),
            "allow_two_segments": lambda v: format_bool(
                "allow_two_segments", v, yesno=True
            ),
            "prefer_zone_connections": lambda v: format_bool(
                "prefer_zone_connections", v, yesno=True
            ),
        }

        for field, formatter in field_specs.items():
            value = getattr(self, field)
            if value is not None:
                expr.append(formatter(value))

        return expr
