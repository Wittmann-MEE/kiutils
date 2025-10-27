"""Unittests of board related classes

Authors:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

import unittest
from os import path
from pathlib import Path
from kiutils.footprint import Attributes

from tests.testfunctions import to_file_and_compare, prepare_test, cleanup_after_test, TEST_BASE
from kiutils.board import Board

BOARD_BASE = path.join(TEST_BASE, 'board')
BOARD_COMMUNITY = path.join(BOARD_BASE, 'community')
BOARD_DEMO = path.join(BOARD_BASE, 'demos')

class Tests_Board_Community(unittest.TestCase):
    """New Test cases for Boards - based on community KiCad projects"""

    def setUp(self):
        prepare_test(self)
        self.testData.compareToTestFile = True
        return super().setUp()

    def test_boardGlasgow(self):
        """Tests the behavior when creating and exporting Glasgow board"""
        self.testData.pathToTestFile = Path(BOARD_COMMUNITY) / 'Glasgow'
        board = Board().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(board, self.testData))

    def test_boardSmartPrintCoreH7x(self):
        """Tests the behavior when creating and exporting SmartPrintCoreH7x board"""
        self.testData.pathToTestFile = Path(BOARD_COMMUNITY) / 'SmartPrintCoreH7x'
        board = Board().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(board, self.testData))

    def test_TokayLite(self):
        """Tests the behavior when creating and exporting TokayLite board"""
        self.testData.pathToTestFile = Path(BOARD_COMMUNITY) / 'TokayLite'
        board = Board().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(board, self.testData))

class Tests_Board_Demos(unittest.TestCase):
    """Test cases for demo boards"""

    def setUp(self):
        prepare_test(self)
        self.testData.compareToTestFile = True
        return super().setUp()

    # def test_RoyalBlue54LFeather(self):
    #     """Tests the behavior when creating and exporting RoyalBlue54L-Feather demo board"""
    #     self.testData.pathToTestFile = Path(BOARD_DEMO) / 'RoyalBlue54L-Feather'
    #     board = Board().from_file(self.testData.pathToTestFile)
    #     self.assertTrue(to_file_and_compare(board, self.testData))

class Tests_Board(unittest.TestCase):
    """Test cases for Boards"""

    def setUp(self) -> None:
        prepare_test(self)
        return super().setUp()
