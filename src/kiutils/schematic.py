"""Class to manage KiCad schematics

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

from typing import Union
from os import path

from kiutils.items.common import Image, PageSettings, TitleBlock
from kiutils.items.schitems import *
from kiutils.symbol import Symbol
from kiutils.utils.sexpr import sexp_prettify as prettify, sexp_to_string, parse_sexp
from kiutils.misc.config import *
from kiutils.utils.parsing_utils import *
from kiutils.utils.string_utils import *


@dataclass
class Schematic:
    """The ``schematic`` token represents a KiCad schematic as defined by the schematic file format

    Documenatation:
        https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/
    """

    version: str = KIUTILS_CREATE_NEW_VERSION_STR
    """The ``version`` token attribute defines the schematic version using the YYYYMMDD date format"""

    generator: str = KIUTILS_CREATE_NEW_GENERATOR_STR
    """The ``generator`` token attribute defines the program used to write the file"""

    uuid: Optional[str] = None
    """The optional ``uuid`` defines the universally unique identifier. Defaults to ``None.``"""

    paper: PageSettings = field(default_factory=lambda: PageSettings())
    """The ``paper`` token defines the drawing page size and orientation"""

    titleBlock: Optional[TitleBlock] = None
    """The ``titleBlock`` token defines author, date, revision, company and comments of the schematic"""

    libSymbols: List[Symbol] = field(default_factory=list)
    """The ``libSymbols`` token defines a list of symbols that are used in the schematic"""

    schematicSymbols: List[SchematicSymbol] = field(default_factory=list)
    """The ``schematicSymbols`` token defines a list of instances of symbols used in the schematic"""

    junctions: List[Junction] = field(default_factory=list)
    """The ``junctions`` token defines a list of junctions used in the schematic"""

    noConnects: List[NoConnect] = field(default_factory=list)
    """The ``noConnect`` token defines a list of no_connect markers used in the schematic"""

    busEntries: List[BusEntry] = field(default_factory=list)
    """The ``busEntries`` token defines a list of bus_entry used in the schematic"""

    busAliases: List[BusAlias] = field(default_factory=list)
    """The ``busAliases`` token defines a list of bus_alias used in the schematic"""

    graphicalItems: List[Union[Connection, PolyLine]] = field(default_factory=list)
    """The ``graphicalItems`` token defines a list of ``bus``, ``wire`` or ``polyline`` elements 
    used in the schematic"""

    shapes: List[Union[Arc, Circle, Rectangle]] = field(default_factory=list)
    """The ``shapes`` token defines a list of graphical shapes (``Arc``, ``Rectangle`` or 
    ``Circle``) used in the schematic.
    
    Available since KiCad v7"""

    images: List[Image] = field(default_factory=list)
    """The ``images`` token defines a list of images used in the schematic"""

    texts: List[Text] = field(default_factory=list)
    """The ``text`` token defines a list of texts used in the schematic"""

    textBoxes: List[TextBox] = field(default_factory=list)
    """The ``text_box`` token defines a list of text boxes used in the schematic"""

    labels: List[LocalLabel] = field(default_factory=list)
    """The ``labels`` token defines a list of local labels used in the schematic"""

    globalLabels: List[GlobalLabel] = field(default_factory=list)
    """The ``globalLabels`` token defines a list of global labels used in the schematic"""

    hierarchicalLabels: List[HierarchicalLabel] = field(default_factory=list)
    """The ``herarchicalLabels`` token defines a list of hierarchical labels used in the schematic"""

    netclassFlags: List[NetclassFlag] = field(default_factory=list)
    """The ``netclassFlags`` token defines a list of netclass flags used in the schematic.
    
    Available since KiCad v7"""

    sheets: List[HierarchicalSheet] = field(default_factory=list)
    """The ``sheets`` token defines a list of hierarchical sheets used in the schematic"""

    sheetInstances: List[HierarchicalSheetInstance] = field(default_factory=list)
    """The ``sheetInstances`` token defines a list of instances of hierarchical sheets used in
    the schematic"""

    symbolInstances: List[SymbolInstance] = field(default_factory=list)
    """The ``symbolInstances`` token defines a list of instances of symbols from ``libSymbols`` token
    used in the schematic"""

    filePath: Optional[str] = None
    """The ``filePath`` token defines the path-like string to the schematic file. Automatically set when
    ``self.from_file()`` is used. Allows the use of ``self.to_file()`` without parameters."""

    # Available since KiCad v9

    generator_version: Optional[str] = None
    """The ``generator_version`` token attribute defines the version of the program used to write the file"""

    embedded_fonts: Optional[bool] = None
    """The ``embeddedFonts`` indicates that there are fonts embedded into this component"""

    tables: list[Table] = field(default_factory=list)
    """The ``tables`` token defines a list of tables used in the schematic"""

    rule_areas: list[PolyLine] = field(default_factory=list)
    """The ``rule_areas`` token defines rule areas used in the schematic"""

    @classmethod
    def from_sexpr(cls, exp: list) -> Schematic:
        """Convert the given S-Expresstion into a Schematic object

        Args:
            - exp (list): Part of parsed S-Expression ``(kicad_sch ...)``

        Raises:
            - Exception: When given parameter's type is not a list
            - Exception: When the first item of the list is not kicad_sch

        Returns:
            - Schematic: Object of the class initialized with the given S-Expression
        """
        if not isinstance(exp, list):
            raise Exception("Expression does not have the correct type")

        if exp[0] != "kicad_sch":
            raise Exception("Expression does not have the correct type")

        object = cls()
        for item in exp[1:]:
            if not isinstance(item, list):
                raise ValueError(
                    f"Expected list property [key, value], got: {item}. Full expression: {exp}"
                )
            elif item[0] == "version":
                object.version = item[1]
            elif item[0] == "generator":
                object.generator = item[1]
            elif item[0] == "generator_version":
                object.generator_version = item[1]
            elif item[0] == "uuid":
                object.uuid = item[1]
            elif item[0] == "paper":
                object.paper = PageSettings().from_sexpr(item)
            elif item[0] == "title_block":
                object.titleBlock = TitleBlock().from_sexpr(item)
            elif item[0] == "lib_symbols":
                for symbol in item[1:]:
                    object.libSymbols.append(Symbol().from_sexpr(symbol))
            elif item[0] == "junction":
                object.junctions.append(Junction().from_sexpr(item))
            elif item[0] == "no_connect":
                object.noConnects.append(NoConnect().from_sexpr(item))
            elif item[0] == "bus_entry":
                object.busEntries.append(BusEntry().from_sexpr(item))
            elif item[0] == "bus_alias":
                object.busAliases.append(BusAlias().from_sexpr(item))
            elif item[0] == "wire":
                object.graphicalItems.append(Connection().from_sexpr(item))
            elif item[0] == "bus":
                object.graphicalItems.append(Connection().from_sexpr(item))
            elif item[0] == "polyline":
                object.graphicalItems.append(PolyLine().from_sexpr(item))
            elif item[0] == "arc":
                object.shapes.append(Arc.from_sexpr(item))
            elif item[0] == "circle":
                object.shapes.append(Circle.from_sexpr(item))
            elif item[0] == "rectangle":
                object.shapes.append(Rectangle.from_sexpr(item))
            elif item[0] == "image":
                object.images.append(Image().from_sexpr(item))
            elif item[0] == "text":
                object.texts.append(Text().from_sexpr(item))
            elif item[0] == "text_box":
                object.textBoxes.append(TextBox().from_sexpr(item))
            elif item[0] == "label":
                object.labels.append(LocalLabel().from_sexpr(item))
            elif item[0] == "global_label":
                object.globalLabels.append(GlobalLabel().from_sexpr(item))
            elif item[0] == "hierarchical_label":
                object.hierarchicalLabels.append(HierarchicalLabel().from_sexpr(item))
            elif item[0] == "netclass_flag":
                object.netclassFlags.append(NetclassFlag.from_sexpr(item))
            elif item[0] == "symbol":
                object.schematicSymbols.append(SchematicSymbol().from_sexpr(item))
            elif item[0] == "sheet":
                object.sheets.append(HierarchicalSheet().from_sexpr(item))
            elif item[0] == "sheet_instances":
                for instance in item[1:]:
                    object.sheetInstances.append(
                        HierarchicalSheetInstance().from_sexpr(instance)
                    )
            elif item[0] == "symbol_instances":
                for instance in item[1:]:
                    object.symbolInstances.append(SymbolInstance().from_sexpr(instance))
            elif item[0] == "embedded_fonts":
                object.embedded_fonts = parse_bool(item, "embedded_fonts")
            elif item[0] == "table":
                object.tables.append(Table().from_sexpr(item))
            elif item[0] == "rule_area":
                object.rule_areas.append(PolyLine().from_sexpr(item[1]))
            else:
                raise ValueError(
                    f"Unrecognized property key: {item[0]}. Full expression: {item}"
                )

        return object

    @classmethod
    def from_file(cls, filepath: str, encoding: Optional[str] = None) -> Schematic:
        """Load a schematic directly from a KiCad schematic file (`.kicad_sch`) and sets the
        ``self.filePath`` attribute to the given file path.

        Args:
            - filepath (str): Path or path-like object that points to the file
            - encoding (str, optional): Encoding of the input file. Defaults to None (platform
                                        dependent encoding).

        Raises:
            - Exception: If the given path is not a file

        Returns:
            - Schematic: Object of the Schematic class initialized with the given KiCad schematic
        """
        if not path.isfile(filepath):
            raise Exception(f"Given path ('{filepath}') is not a file!")

        with open(filepath, "r", encoding=encoding) as infile:
            item = cls.from_sexpr(parse_sexp(infile.read()))
            item.filePath = filepath
            return item

    @classmethod
    def create_new(cls) -> Schematic:
        """Creates a new empty schematic page with its attributes set as KiCad would create it

        Returns:
            - Schematic: Empty schematic
        """
        schematic = Schematic()
        schematic.version = KIUTILS_CREATE_NEW_VERSION_STR
        schematic.generator = KIUTILS_CREATE_NEW_GENERATOR_STR
        schematic.generator_version = KIUTILS_CREATE_NEW_GENERATOR_VERSION_STR
        schematic.sheetInstances.append(
            HierarchicalSheetInstance(instancePath="/", page="1")
        )
        schematic.embedded_fonts = False
        return schematic

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

    def to_sexpr(self, indent=0, newline=True) -> str:
        """Generate the S-Expression representing this object

        Args:
            - indent (int): Number of whitespaces used to indent the output. Defaults to 0.
            - newline (bool): Adds a newline to the end of the output. Defaults to True.

        Returns:
            - str: S-Expression of this object
        """
        raw_expr = self._to_sexpr_raw()
        return sexp_to_string(raw_expr)

    def _to_sexpr_raw(self):
        expr = [
            "kicad_sch",
            ["version", self.version],
            ["generator", quote(self.generator)],
        ]

        if self.generator_version is not None:
            expr.append(["generator_version", quote(self.generator_version)])

        if self.uuid is not None:
            expr.append(["uuid", quote(self.uuid)])

        expr.append(self.paper._to_sexpr_raw())

        if self.titleBlock is not None:
            expr.append(self.titleBlock._to_sexpr_raw())

        if self.libSymbols:
            expr.append(
                ["lib_symbols"] + [item._to_sexpr_raw() for item in self.libSymbols]
            )
        else:
            expr.append(["lib_symbols"])

        if self.busAliases:
            expr.extend(item._to_sexpr_raw() for item in self.busAliases)
        if self.texts:
            expr.extend(item._to_sexpr_raw() for item in self.texts)
        if self.textBoxes:
            expr.extend(item._to_sexpr_raw() for item in self.textBoxes)
        if self.junctions:
            expr.extend(item._to_sexpr_raw() for item in self.junctions)
        if self.noConnects:
            expr.extend(item._to_sexpr_raw() for item in self.noConnects)
        if self.busEntries:
            expr.extend(item._to_sexpr_raw() for item in self.busEntries)
        if self.graphicalItems:
            expr.extend(item._to_sexpr_raw() for item in self.graphicalItems)
        if self.tables:
            expr.extend(item._to_sexpr_raw() for item in self.tables)
        if self.shapes:
            expr.extend(item._to_sexpr_raw() for item in self.shapes)
        if self.images:
            expr.extend(item._to_sexpr_raw() for item in self.images)
        if self.labels:
            expr.extend(item._to_sexpr_raw() for item in self.labels)
        if self.globalLabels:
            expr.extend(item._to_sexpr_raw() for item in self.globalLabels)
        if self.hierarchicalLabels:
            expr.extend(item._to_sexpr_raw() for item in self.hierarchicalLabels)

        if len(self.rule_areas) > 0:
            for ra in self.rule_areas:
                expr.append(["rule_area", ra._to_sexpr_raw()])

        if self.netclassFlags:
            expr.extend(item._to_sexpr_raw() for item in self.netclassFlags)

        if self.schematicSymbols:
            expr.extend(item._to_sexpr_raw() for item in self.schematicSymbols)

        if self.sheets:
            expr.extend(item._to_sexpr_raw() for item in self.sheets)

        if self.sheetInstances:
            expr.append(
                ["sheet_instances"]
                + [item._to_sexpr_raw() for item in self.sheetInstances]
            )

        if self.symbolInstances:
            expr.append(
                ["symbol_instances"]
                + [item._to_sexpr_raw() for item in self.symbolInstances]
            )

        if self.embedded_fonts is not None:
            expr.append(
                format_bool(
                    "embedded_fonts", self.embedded_fonts, compact=False, yesno=True
                )
            )

        return expr
