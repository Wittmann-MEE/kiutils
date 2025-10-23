"""Unittests of schematic related classes

Authors:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

import unittest
from os import path
from pathlib import Path
from kiutils.items.schitems import HierarchicalSheetInstance

from tests.testfunctions import to_file_and_compare, prepare_test, cleanup_after_test, TEST_BASE
from kiutils.schematic import Schematic
from kiutils.items.common import Property

SCHEMATIC_BASE = path.join(TEST_BASE, 'schematic')
SCHEMATIC_COMMUNITY = path.join(SCHEMATIC_BASE, 'community')
SCHEMATIC_DEMO = path.join(SCHEMATIC_BASE, 'demos')

class Tests_Schematic_Community(unittest.TestCase):
    """New Test cases for Schematics - based on community KiCad projects"""

    def setUp(self) -> None:
        prepare_test(self)
        self.testData.compareToTestFile = True
        return super().setUp()

    def test_Glasgow(self):
        """Tests the behavior when creating and exporting Glasgow schematic"""
        self.testData.pathToTestFile = Path(SCHEMATIC_COMMUNITY) / 'Glasgow'
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))

    def test_SmartPrintCoreH7x(self):
        """Tests the behavior when creating and exporting SmartPrintCoreH7x schematic"""
        self.testData.pathToTestFile = Path(SCHEMATIC_COMMUNITY) / 'SmartPrintCoreH7x'
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))

    def test_TokayLite(self):
        """Tests the behavior when creating and exporting TokayLite schematic"""
        self.testData.pathToTestFile = Path(SCHEMATIC_COMMUNITY) / 'TokayLite'
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
        self.testData.pathToTestFile = Path(SCHEMATIC_DEMO) / 'RoyalBlue54L-Feather'
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))


class Tests_Schematic(unittest.TestCase):
    """Test cases for Schematics"""

    def setUp(self) -> None:
        prepare_test(self)
        return super().setUp()
