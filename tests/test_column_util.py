import os
import sys
import pytest

# Ensure src/ is on sys.path
ROOT = os.path.dirname(__file__)
SRC  = os.path.join(ROOT, "..", "src")
sys.path.insert(0, SRC)

from utilities.ColumnUtil import ColumnUtil


@pytest.mark.parametrize("input_col, expected", [
    ("`col`",    "col"),
    ("col",      "col"),
    ("`a.b.c`",  "a.b.c"),
    ("`x`",      "x"),
])
def test_remove_escape_column(input_col, expected):
    assert ColumnUtil.remove_escape_column(input_col) == expected


@pytest.mark.parametrize("input_col, expected", [
    ("col",      "col"),
    ("a.b.c",    "`a.b.c`"),
    ("no.dot",   "no.dot"),
    ("already`", "`already`"),  # edge: contains backtick but no leading/trailing
])
def test_escape_column(input_col, expected):
    assert ColumnUtil.escape_column(input_col) == expected
