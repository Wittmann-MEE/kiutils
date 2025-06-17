"""Helper functions for the unittests

Authors:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

from dataclasses import dataclass
from typing import Optional
import filecmp
import os
import tempfile
import shutil

TEST_BASE = os.path.join('tests', 'testdata')

@dataclass
class TestData():
    """Data container to relay testcase-specific information to the report generator. May be added
    as a member to ``unittest.TestCase`` in the ``setUp()`` function. The object will then be
    available in ``result._TestInfo()`` classes constructor."""
    producedOutput: Optional[str] = None
    expectedOutput: Optional[str] = None
    ownDescription: Optional[str] = None
    pathToTestFile: Optional[str] = None
    compareToTestFile: bool = False
    wasSuccessful: bool = False


def to_file_and_compare(object, test_data: TestData) -> bool:
    """Write the object to a file using its ``to_file()`` method and comparing the output with
    the given expected output supplied by a file with ``.expected`` suffix

    Cleans up the test files afterwards, leaving only failing test outputs behind. Test output
    is furthermore saved to ``test_data.expectedOutput`` and ``test_data.producedOutput`` to be
    displayed in the HTML test report.

    Args:
        - object: KiUtils object with a ``to_file()`` method
        - test_data (TestData): Test data object of the currently running test (contains path to 
                                test file)

    Returns:
        - bool: True, if both the output of ``to_file()`` and the given expected output are the same
    """
    # Create S-Expression from object
    if test_data.pathToTestFile is None:
        raise Exception("pathToTestFile may not be None!")

    tmp_dir = tempfile.mkdtemp(prefix="test_", dir=os.getcwd())  # or use a fixed ./tmp/
    output_file = os.path.join(tmp_dir, f'{os.path.basename(test_data.pathToTestFile)}.testoutput')

    object.to_file(output_file)

    # Compare with the expected result
    if test_data.compareToTestFile:
        compare_file = test_data.pathToTestFile
    else:
        compare_file = f'{test_data.pathToTestFile}.expected'

    test_data.wasSuccessful = filecmp.cmp(output_file, compare_file)
    cleanup_after_test(test_data, tmp_dir)
    return test_data.wasSuccessful

def load_contents(file: str) -> str:
    """Load contents of a specific file and return it as a joined string

    Args:
        file (str): Path to file

    Returns:
        str: Contents of file in one string
    """
    with open(file, "r") as outfile:
        return ''.join(outfile.readlines())

def prepare_test(object):
    """Prepare a unittest test case in the KiUtils framework

    Args:
        object: Test case class object
    """
    object.testData = TestData()

def cleanup_after_test(test_data: TestData, tmp_dir: str):
    """Cleanup after a unittest test case ran

    Args:
        test_data (TestData): Test data structure of test case that finished last

    Raises:
        Exception: When ``test_data.pathToTestFile`` is None
    """
    if test_data.pathToTestFile is None:
        raise Exception("Path to testfile must not be None!")

    if test_data.wasSuccessful:
        shutil.rmtree(tmp_dir)