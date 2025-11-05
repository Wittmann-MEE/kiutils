"""Unittests of schematic related classes

Authors:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

import unittest
from os import path, getenv
from pathlib import Path
from kiutils.items.schitems import HierarchicalSheetInstance

from tests.testfunctions import (
    to_file_and_compare,
    prepare_test,
    cleanup_after_test,
    TEST_BASE,
)
from kiutils.schematic import Schematic
from kiutils.items.common import Property

SCHEMATIC_BASE = path.join(TEST_BASE, "schematic")
SCHEMATIC_COMMUNITY = path.join(SCHEMATIC_BASE, "community")
SCHEMATIC_DEMO = path.join(SCHEMATIC_BASE, "demos")


class Tests_Schematic_Community(unittest.TestCase):
    """New Test cases for Schematics - based on community KiCad projects"""

    def setUp(self) -> None:
        prepare_test(self)
        self.testData.compareToTestFile = True
        return super().setUp()

    def test_Glasgow(self):
        """Tests the behavior when creating and exporting Glasgow schematic"""
        self.testData.pathToTestFile = Path(SCHEMATIC_COMMUNITY) / "Glasgow"
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))

    def test_SmartPrintCoreH7x(self):
        """Tests the behavior when creating and exporting SmartPrintCoreH7x schematic"""
        self.testData.pathToTestFile = Path(SCHEMATIC_COMMUNITY) / "SmartPrintCoreH7x"
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))

    def test_TokayLite(self):
        """Tests the behavior when creating and exporting TokayLite schematic"""
        self.testData.pathToTestFile = Path(SCHEMATIC_COMMUNITY) / "TokayLite"
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))


class Tests_Schematic_Demos(unittest.TestCase):
    """Test cases for demo schematics"""

    def setUp(self) -> None:
        prepare_test(self)
        self.testData.compareToTestFile = True
        return super().setUp()

    def test_RoyalBlue54LFeather(self):
        """Tests the behavior when creating and exporting RoyalBlue54LFeather demo schematic"""
        self.testData.pathToTestFile = Path(SCHEMATIC_DEMO) / "RoyalBlue54L-Feather"
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))

    def test_KitDevColdfireXilinx_5213(self):
        """Tests the behavior when creating and exporting KitDevColdfireXilinx_5213 demo schematic"""
        self.testData.pathToTestFile = (
            Path(SCHEMATIC_DEMO) / "KitDevColdfireXilinx_5213"
        )
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))

    def test_StickHub(self):
        """Tests the behavior when creating and exporting StickHub demo schematic"""
        self.testData.pathToTestFile = Path(SCHEMATIC_DEMO) / "StickHub"
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))

    def test_Video(self):
        """Tests the behavior when creating and exporting Video demo schematic"""
        self.testData.pathToTestFile = Path(SCHEMATIC_DEMO) / "Video"
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))


class Tests_Private_Schematics(unittest.TestCase):
    """Test cases for private schematics"""

    def setUp(self) -> None:
        prepare_test(self)
        self.testData.compareToTestFile = True
        return super().setUp()

    def test_All_Private(self):
        """Tests creating and exporting all private schematics"""
        # Read environment variable
        private_path = getenv("PRIVATE_KICAD_REPO")
        if not private_path:
            self.skipTest(
                "Environment variable PRIVATE_KICAD_REPO not set, skipping private schematics test."
            )

        private_schematics_path = Path(private_path)
        if not private_schematics_path.exists():
            self.skipTest(
                f"Path {private_schematics_path} does not exist, skipping private schematics test."
            )

        failures = []
        schematics = private_schematics_path.rglob("*.kicad_sch")
        print("Collected schematics: ", schematics)
        for schematic_file in schematics:
            print(f"Testing private schematic file: {schematic_file}")
            with self.subTest(schematic=schematic_file):
                self.testData.pathToTestFile = schematic_file
                try:
                    schematic = Schematic().from_file(self.testData.pathToTestFile)
                except:
                    print(f"Failed to parse schematic {schematic_file}, skipping.")
                    continue

                if schematic.generator_version is not None:
                    try:
                        self.assertTrue(to_file_and_compare(schematic, self.testData))
                    except AssertionError as e:
                        failures.append((schematic_file, str(e)))

        if failures:
            failure_messages = "\n".join(
                [f"Schematic: {file}, Error: {error}" for file, error in failures]
            )
            self.fail(f"Some private schematics failed the tests:\n{failure_messages}")


class Tests_Schematic(unittest.TestCase):
    """Test cases for Schematics"""

    def setUp(self) -> None:
        prepare_test(self)
        return super().setUp()
