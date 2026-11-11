"""Native schematic formatting must depend on field context and file version."""

from pathlib import Path
import tempfile
import unittest

from kiutils.items.common import Effects, Property
from kiutils.items.schitems import (
    GlobalLabel,
    HierarchicalLabel,
    HierarchicalSheet,
    LocalLabel,
    NetclassFlag,
    SchematicSymbol,
)
from kiutils.schematic import Schematic
from kiutils.symbol import Symbol, SymbolLib
from kiutils.utils.sexpr import parse_sexp


class Tests_NativeSchematicFormatting(unittest.TestCase):
    def schematic(self, version=20250114):
        source = f"""(kicad_sch
            (version {version}) (generator "eeschema") (generator_version "9.0")
            (uuid "root") (paper "A4")
            (lib_symbols (symbol "test:part"
                (property "Reference" "R" (at 0 0 0) (show_name) (do_not_autoplace))))
            (wire (pts (xy 1 2) (xy 3 4))
                (stroke (width 0) (type default)) (uuid "wire"))
            (bus (pts (xy 1 2) (xy 3 4))
                (stroke (width 0) (type default)) (uuid "bus"))
            (rectangle (start 1 2) (end 3 4)
                (stroke (width 0) (type default)) (fill (type none)) (uuid "rect"))
            (arc (start 1 2) (mid 2 3) (end 3 4)
                (stroke (width 0) (type default)) (fill (type none)) (uuid "arc"))
            (circle (center 1 2) (radius 3)
                (stroke (width 0) (type default)) (fill (type none)) (uuid "circle"))
            (polyline (pts (xy 1 2) (xy 3 4))
                (stroke (width 0) (type default)) (uuid "notes-line"))
            (polyline (pts (xy 1 2) (xy 3 4) (xy 5 6))
                (stroke (width 0) (type default)) (fill (type none)) (uuid "polygon"))
            (rule_area (polyline (pts (xy 1 2) (xy 3 4) (xy 5 6))
                (stroke (width 0) (type default)) (fill (type none)) (uuid "area")))
            (symbol (lib_id "test:part") (at 1 2 0) (unit 1)
                (in_bom yes) (on_board yes) (dnp no) (uuid "symbol")
                (property "Value" "µC (do_not_autoplace)"
                    (at 1 2 0) (show_name yes) (do_not_autoplace yes)
                    (effects (font (size 1 1)))))
            (embedded_fonts no))"""
        return Schematic.from_sexpr(parse_sexp(source))

    def test_native_kicad9_shape_uuid_context(self):
        text = self.schematic().to_sexpr()
        for uuid in ("rect", "arc", "circle", "polygon", "area"):
            self.assertIn(f"(uuid {uuid})", text)
        for uuid in ("root", "notes-line", "symbol", "wire", "bus"):
            self.assertIn(f'(uuid "{uuid}")', text)

    def test_kicad10_keeps_quoted_shape_uuids(self):
        text = self.schematic(20260101).to_sexpr()
        for uuid in ("rect", "arc", "circle", "polygon", "area", "notes-line"):
            self.assertIn(f'(uuid "{uuid}")', text)

    def test_fields_and_library_cache_use_their_native_flag_forms(self):
        expression = parse_sexp(self.schematic().to_sexpr())
        library = next(
            n for n in expression if isinstance(n, list) and n[0] == "lib_symbols"
        )
        cached = library[1][2]
        self.assertIn(["show_name"], cached)
        self.assertIn(["do_not_autoplace"], cached)
        placed = next(n for n in expression if isinstance(n, list) and n[0] == "symbol")
        prop = next(n for n in placed if isinstance(n, list) and n[0] == "property")
        self.assertIn(["show_name", "yes"], prop)
        self.assertIn(["do_not_autoplace", "yes"], prop)
        self.assertEqual("µC (do_not_autoplace)", prop[2])

    def test_all_placed_field_owners_use_explicit_flags(self):
        for owner in (
            LocalLabel,
            GlobalLabel,
            HierarchicalLabel,
            NetclassFlag,
            SchematicSymbol,
        ):
            with self.subTest(owner=owner.__name__):
                item = owner()
                if owner is NetclassFlag:
                    item.effects = Effects()
                item.properties.append(
                    Property(
                        key="Field", value="Value", showName=True, do_not_autoplace=True
                    )
                )
                text = item.to_sexpr()
                self.assertIn("(show_name yes)", text)
                self.assertIn("(do_not_autoplace yes)", text)
        sheet = HierarchicalSheet()
        sheet.sheetName.do_not_autoplace = True
        sheet.fileName.do_not_autoplace = True
        sheet.properties.append(Property(key="Field", do_not_autoplace=True))
        self.assertEqual(3, sheet.to_sexpr().count("(do_not_autoplace yes)"))

    def test_symbol_library_flags_are_compact(self):
        symbol = Symbol(
            entryName="part",
            properties=[Property(key="Field", showName=True, do_not_autoplace=True)],
        )
        text = SymbolLib(symbols=[symbol]).to_sexpr()
        self.assertIn("(show_name)", text)
        self.assertIn("(do_not_autoplace)", text)

    def test_changing_version_and_saving_does_not_mutate_items(self):
        schematic = self.schematic()
        first = schematic.to_sexpr()
        schematic.version = 20260101
        self.assertIn('(uuid "rect")', schematic.to_sexpr())
        schematic.version = 20250114
        self.assertEqual(first, schematic.to_sexpr())
        self.assertEqual("rect", schematic.shapes[0].uuid)
        self.assertTrue(schematic.schematicSymbols[0].properties[0].do_not_autoplace)

    def test_direct_file_roundtrip_is_stable_with_unicode(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.kicad_sch"
            self.schematic().to_file(str(path), encoding="utf-8")
            first = path.read_bytes()
            for _ in range(3):
                Schematic.from_file(str(path), encoding="utf-8").to_file(
                    str(path), encoding="utf-8"
                )
                self.assertEqual(first, path.read_bytes())


if __name__ == "__main__":
    unittest.main()
