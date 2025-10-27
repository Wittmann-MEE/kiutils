"""Unittests of board related classes

Authors:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

import unittest
from os import path, getenv
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

    def test_RoyalBlue54LFeather(self):
        """Tests the behavior when creating and exporting RoyalBlue54L-Feather demo board"""
        self.testData.pathToTestFile = Path(BOARD_DEMO) / 'RoyalBlue54L-Feather'
        board = Board().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(board, self.testData))

    def test_KitDevColdfireXilinx_5213(self):
        """Tests the behavior when creating and exporting KitDevColdfireXilinx_5213 demo board"""
        self.testData.pathToTestFile = Path(BOARD_DEMO) / 'KitDevColdfireXilinx_5213'
        board = Board().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(board, self.testData))

    def test_StickHub(self):
        """Tests the behavior when creating and exporting StickHub demo board"""
        self.testData.pathToTestFile = Path(BOARD_DEMO) / 'StickHub'
        board = Board().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(board, self.testData))

    def test_Video(self):
        """Tests the behavior when creating and exporting Video demo board"""
        self.testData.pathToTestFile = Path(BOARD_DEMO) / 'Video'
        board = Board().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(board, self.testData))

class Tests_Private_Boards(unittest.TestCase):
    """Test cases for private boards"""

    def setUp(self) -> None:
        prepare_test(self)
        self.testData.compareToTestFile = True
        return super().setUp()

    def test_all_private(self):
        """Tests creating and exporting all private boards"""
        # Read environment variable
        private_path = getenv("PRIVATE_KICAD_REPO")
        if not private_path:
            self.skipTest("Environment variable PRIVATE_KICAD_REPO not set, skipping private boards test.")

        private_boards_path = Path(private_path)
        if not private_boards_path.exists():
            self.skipTest(f"Path {private_boards_path} does not exist, skipping private boards test.")
        
        failures = []
        for board_file in private_boards_path.rglob('*.kicad_pcb'):
            print(f"Testing private board file: {board_file}")
            with self.subTest(board=board_file):
                self.testData.pathToTestFile = board_file
                try:
                    board = Board().from_file(self.testData.pathToTestFile)
                except:
                    print(f"Failed to parse board {board_file}, skipping.")
                    continue

                if board.generator_version is not None:
                    try:
                        self.assertTrue(to_file_and_compare(board, self.testData))
                    except AssertionError as e:
                        failures.append((board_file, str(e)))
        
        if failures:
            failure_messages = "\n".join([f"Board: {file}, Error: {error}" for file, error in failures])
            self.fail(f"Some private boards failed the tests:\n{failure_messages}")


class Tests_Board(unittest.TestCase):
    """Test cases for Boards"""

    def setUp(self) -> None:
        prepare_test(self)
        return super().setUp()
