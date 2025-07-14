# -----------------------------------------------------------------------------
# PyDeequ — 100% Python port of Amazon Deequ
# Author: AMIR HOSSEIN ALIKHAH MISHAMANDANI
# Email: amirhosseinalikhahm@gatech.edu
# Created: 2025-07-14
# version: 0.0.1
# -----------------------------------------------------------------------------
#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
# -----------------------------------------------------------------------------
#
# © 2025 Neuroligence. Licensed under the MIT License.
# See the LICENSE file in the project root for the full MIT terms.
# -----------------------------------------------------------------------------

import pandas as pd
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple
from dataclasses import dataclass


class ColumnDefinition:
    """Base for per-column schema definitions."""

    def __init__(self, name: str, is_nullable: bool = True):
        self.name = name
        self.is_nullable = is_nullable

    def is_valid(self, series: pd.Series) -> pd.Series:
        return pd.Series(True, index=series.index) if self.is_nullable else series.notnull()

    def cast_series(self, series: pd.Series) -> pd.Series:
        return series


class StringColumnDefinition(ColumnDefinition):
    def __init__(
            self,
            name: str,
            is_nullable: bool = True,
            min_length: Optional[int] = None,
            max_length: Optional[int] = None,
            matches: Optional[str] = None
    ):
        super().__init__(name, is_nullable)
        self.min_length = min_length
        self.max_length = max_length
        self.matches = matches

    def is_valid(self, series: pd.Series) -> pd.Series:
        s = series.astype(object)
        # Always enforce type (string or null)
        mask = s.isnull() | s.apply(lambda x: isinstance(x, str))

        if not self.is_nullable:
            # enforce non-null
            mask &= s.notnull()
            # enforce length constraints
            if self.min_length is not None:
                mask &= s.str.len().ge(self.min_length)
            if self.max_length is not None:
                mask &= s.str.len().le(self.max_length)
            # enforce regex
            if self.matches is not None:
                mask &= s.str.match(self.matches)

        return mask


class IntColumnDefinition(ColumnDefinition):
    def __init__(
            self,
            name: str,
            is_nullable: bool = True,
            min_value: Optional[int] = None,
            max_value: Optional[int] = None
    ):
        super().__init__(name, is_nullable)
        self.min_value = min_value
        self.max_value = max_value

    def is_valid(self, series: pd.Series) -> pd.Series:
        coerced = pd.to_numeric(series, errors="coerce").astype("Int64")
        mask = pd.Series(True, index=series.index)

        if self.is_nullable:
            mask &= (series.isnull() | coerced.notnull())
        else:
            mask &= coerced.notnull()

        if self.min_value is not None:
            mask &= (series.isnull() | coerced.ge(self.min_value))
        if self.max_value is not None:
            mask &= (series.isnull() | coerced.le(self.max_value))

        return mask

    def cast_series(self, series: pd.Series) -> pd.Series:
        return pd.to_numeric(series, errors="coerce").astype("Int64")


class DecimalColumnDefinition(ColumnDefinition):
    def __init__(
            self,
            name: str,
            precision: int,
            scale: int,
            is_nullable: bool = True
    ):
        super().__init__(name, is_nullable)
        self.precision = precision
        self.scale = scale

    def is_valid(self, series: pd.Series) -> pd.Series:
        def check_decimal(x: any) -> bool:
            if pd.isnull(x):
                return self.is_nullable
            try:
                d = Decimal(str(x))
            except InvalidOperation:
                return False
            digits = d.as_tuple().digits
            if len(digits) > self.precision:
                return False
            if -d.as_tuple().exponent > self.scale:
                return False
            return True

        return series.apply(check_decimal)

    def cast_series(self, series: pd.Series) -> pd.Series:
        return series.apply(lambda x: Decimal(str(x)) if pd.notnull(x) else None)


class TimestampColumnDefinition(ColumnDefinition):
    def __init__(
            self,
            name: str,
            mask: str,
            is_nullable: bool = True
    ):
        super().__init__(name, is_nullable)
        self.mask = mask

    def is_valid(self, series: pd.Series) -> pd.Series:
        coerced = pd.to_datetime(series, format=self.mask, errors="coerce")
        if self.is_nullable:
            return series.isnull() | coerced.notnull()
        return coerced.notnull()

    def cast_series(self, series: pd.Series) -> pd.Series:
        return pd.to_datetime(series, format=self.mask, errors="coerce")


@dataclass(frozen=True)
class RowLevelSchema:
    column_definitions: Tuple[ColumnDefinition, ...] = ()

    def with_string_column(
            self,
            name: str,
            is_nullable: bool = True,
            min_length: Optional[int] = None,
            max_length: Optional[int] = None,
            matches: Optional[str] = None
    ) -> "RowLevelSchema":
        return RowLevelSchema(
            self.column_definitions + (
                StringColumnDefinition(name, is_nullable, min_length, max_length, matches),
            )
        )

    def with_int_column(
            self,
            name: str,
            is_nullable: bool = True,
            min_value: Optional[int] = None,
            max_value: Optional[int] = None
    ) -> "RowLevelSchema":
        return RowLevelSchema(
            self.column_definitions + (
                IntColumnDefinition(name, is_nullable, min_value, max_value),
            )
        )

    def with_decimal_column(
            self,
            name: str,
            precision: int,
            scale: int,
            is_nullable: bool = True
    ) -> "RowLevelSchema":
        return RowLevelSchema(
            self.column_definitions + (
                DecimalColumnDefinition(name, precision, scale, is_nullable),
            )
        )

    def with_timestamp_column(
            self,
            name: str,
            mask: str,
            is_nullable: bool = True
    ) -> "RowLevelSchema":
        return RowLevelSchema(
            self.column_definitions + (
                TimestampColumnDefinition(name, mask, is_nullable),
            )
        )


@dataclass(frozen=True)
class RowLevelSchemaValidationResult:
    valid_rows: pd.DataFrame
    num_valid_rows: int
    invalid_rows: pd.DataFrame
    num_invalid_rows: int


class RowLevelSchemaValidator:
    """Enforce a RowLevelSchema on a pandas DataFrame."""

    @staticmethod
    def validate(
            data: pd.DataFrame,
            schema: RowLevelSchema
    ) -> RowLevelSchemaValidationResult:
        df = data.copy()
        mask = pd.Series(True, index=df.index)

        for cd in schema.column_definitions:
            series = df.get(cd.name, pd.Series([None] * len(df), index=df.index))
            mask &= cd.is_valid(series)

        valid = df[mask].copy()
        invalid = df[~mask].copy()

        casted = {}
        defined_names = [cd.name for cd in schema.column_definitions]
        for cd in schema.column_definitions:
            casted[cd.name] = cd.cast_series(valid[cd.name])

        for col in valid.columns:
            if col not in defined_names:
                casted[col] = valid[col]

        valid_casted_df = pd.DataFrame(casted, index=valid.index)
        return RowLevelSchemaValidationResult(
            valid_rows=valid_casted_df,
            num_valid_rows=valid_casted_df.shape[0],
            invalid_rows=invalid,
            num_invalid_rows=invalid.shape[0]
        )
