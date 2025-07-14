import os
import sys

import pandas as pd
import pytest
from decimal import Decimal

# Make sure src/ is on the import path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from schema.RowLevelSchemaValidator import (
    ColumnDefinition,
    StringColumnDefinition,
    IntColumnDefinition,
    DecimalColumnDefinition,
    TimestampColumnDefinition,
    RowLevelSchema,
    RowLevelSchemaValidator,
    RowLevelSchemaValidationResult,
)


def test_base_column_definition():
    series = pd.Series([1, None, "x"])
    # nullable → all True
    cd = ColumnDefinition("c", is_nullable=True)
    mask = cd.is_valid(series)
    assert mask.tolist() == [True, True, True]
    # not nullable → only non-null
    cd_nn = ColumnDefinition("c", is_nullable=False)
    mask2 = cd_nn.is_valid(series)
    assert mask2.tolist() == [True, False, True]


@pytest.mark.parametrize("values,is_nullable,exp", [
    (["ab", "a", None, 123], True,  [True, True, True, False]),
    (["ab", "a", None, "xyz"], False, [True, False, False, True]),
])
def test_string_column_min_max_and_nullable(values, is_nullable, exp):
    series = pd.Series(values)
    scd = StringColumnDefinition(
        name="s", is_nullable=is_nullable,
        min_length=2, max_length=3
    )
    mask = scd.is_valid(series)
    assert mask.tolist() == exp


def test_string_column_regex():
    series = pd.Series(["foo", "bar", "baz", None])
    scd = StringColumnDefinition("s", is_nullable=False, matches="ba.")
    mask = scd.is_valid(series)
    # only "bar" and "baz" match; foo, None → invalid because is_nullable=False
    assert mask.tolist() == [False, True, True, False]


@pytest.mark.parametrize("values,is_nullable,exp", [
    (["1", "two", None, "5"], True,  [True, False, True, True]),
    (["1", "two", None, "5"], False, [True, False, False, True]),
])
def test_int_column_nullable_and_parse(values, is_nullable, exp):
    series = pd.Series(values)
    icd = IntColumnDefinition("i", is_nullable=is_nullable)
    mask = icd.is_valid(series)
    assert mask.tolist() == exp


def test_int_column_min_max():
    series = pd.Series(["0", "1", "5", "6"])
    icd = IntColumnDefinition("i", min_value=1, max_value=5)
    # "0" < 1, "6" > 5
    assert icd.is_valid(series).tolist() == [False, True, True, False]


@pytest.mark.parametrize("values,exp", [
    (["1.23", "12.3", "123.45", "1234", None, "bad"], [True, True, False, False, True, False]),
])
def test_decimal_column_precision_scale(values, exp):
    series = pd.Series(values)
    dcd = DecimalColumnDefinition("d", precision=3, scale=2)
    assert dcd.is_valid(series).tolist() == exp


def test_decimal_column_cast():
    series = pd.Series(["1.20", None, "3.5"])
    dcd = DecimalColumnDefinition("d", precision=3, scale=2)
    casted = dcd.cast_series(series)
    assert isinstance(casted[0], Decimal)
    assert casted[1] is None
    assert isinstance(casted[2], Decimal)


@pytest.mark.parametrize("values,is_nullable,exp", [
    (["2025-07-14", "bad", None], True,  [True, False, True]),
    (["2025-07-14", "bad", None], False, [True, False, False]),
])
def test_timestamp_column_parse(values, is_nullable, exp):
    series = pd.Series(values)
    tcd = TimestampColumnDefinition("t", mask="%Y-%m-%d", is_nullable=is_nullable)
    mask = tcd.is_valid(series)
    assert mask.tolist() == exp


def test_timestamp_column_cast():
    series = pd.Series(["2025-07-14", None])
    tcd = TimestampColumnDefinition("t", mask="%Y-%m-%d")
    casted = tcd.cast_series(series)
    assert pd.api.types.is_datetime64_ns_dtype(casted.dtype)
    assert casted.iloc[1] is pd.NaT


def test_full_row_level_validation():
    df = pd.DataFrame({
        "s":    ["ab",     "a",      "abc"],
        "i":    ["1",      "2",      "3"],
        "d":    ["1.2",    "invalid","12.345"],
        "t":    ["2025-07-14", "bad", "2025-07-13"],
        "extra":[10,        20,      30]
    })

    schema = (
        RowLevelSchema()
        .with_string_column("s", is_nullable=False, min_length=2, max_length=3)
        .with_int_column("i", min_value=1, max_value=3)
        .with_decimal_column("d", precision=3, scale=2)
        .with_timestamp_column("t", mask="%Y-%m-%d", is_nullable=False)
    )

    result = RowLevelSchemaValidator.validate(df, schema)

    # Only row 0 is fully valid
    assert isinstance(result, RowLevelSchemaValidationResult)
    assert result.num_valid_rows == 1
    assert result.num_invalid_rows == 2

    # Check valid DataFrame
    valid = result.valid_rows
    assert list(valid.index) == [0]
    # Casted types
    assert pd.api.types.is_integer_dtype(valid["i"].dtype)
    assert all(isinstance(x, Decimal) for x in valid["d"])
    assert pd.api.types.is_datetime64_ns_dtype(valid["t"].dtype)
    # Extra column preserved
    assert valid["extra"].iloc[0] == 10

    # Invalid rows contain indices 1 and 2
    invalid = result.invalid_rows
    assert set(invalid.index) == {1, 2}
