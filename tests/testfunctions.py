"""Helper functions for the unittests.

Authors:
    (C) Marvin Mager - @mvnmgrx - 2022

License:
    GPL-3.0
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import filecmp
import tempfile
import shutil
import stat
import os

TEST_BASE = Path('tests') / 'testdata'


@dataclass
class TestData:
    """Data container for testcase-specific information used in test reports."""
    producedOutput: Optional[str] = None
    expectedOutput: Optional[str] = None
    ownDescription: Optional[str] = None
    pathToTestFile: Optional[Path] = None
    compareToTestFile: bool = False
    wasSuccessful: bool = False


def to_file_and_compare(obj, test_data: TestData) -> bool:
    """
    Writes the object to a file via its `to_file()` method, then compares the result
    with the expected file contents.

    If the test passes, the temporary directory is removed. If it fails, output remains.

    Args:
        obj: Object with a `.to_file(output_path)` method.
        test_data (TestData): Information about the test case.

    Returns:
        bool: True if output matches expected, False otherwise.
    """
    if test_data.pathToTestFile is None:
        raise ValueError("`test_data.pathToTestFile` must not be None.")

    tmp_dir = Path(tempfile.mkdtemp(prefix="test_", dir=Path.cwd()))
    output_file = tmp_dir / f"{test_data.pathToTestFile.name}.testoutput"

    obj.to_file(str(output_file))

    # Determine which file to compare against
    compare_file = (
        test_data.pathToTestFile
        if test_data.compareToTestFile
        else test_data.pathToTestFile.with_suffix(".expected")
    )

    test_data.producedOutput = load_contents(output_file)
    test_data.expectedOutput = load_contents(compare_file) if compare_file.exists() else None
    test_data.wasSuccessful = filecmp.cmp(output_file, compare_file, shallow=False)

    cleanup_after_test(test_data, tmp_dir)
    return test_data.wasSuccessful


def load_contents(file: Path) -> str:
    """Reads the contents of a file and returns them as a single string."""
    with file.open("r", encoding="utf-8") as f:
        return f.read()


def prepare_test(test_case_obj):
    """Initializes `testData` for a unittest test case class."""
    test_case_obj.testData = TestData()


def cleanup_after_test(test_data: TestData, tmp_dir: Path):
    """
    Cleans up the temporary test directory unless the test failed.

    Args:
        test_data (TestData): Information about the test case.
        tmp_dir (Path): Path to the temporary test directory.
    """
    if test_data.pathToTestFile is None:
        raise ValueError("`test_data.pathToTestFile` must not be None.")

    if test_data.wasSuccessful:
        shutil.rmtree(tmp_dir)
