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

class ColumnUtil:
    """Utility class for column name operations."""

    @staticmethod
    def remove_escape_column(column: str) -> str:
        """Remove escape characters from column name if present."""
        if column.startswith("`") and column.endswith("`"):
            return column[1:-1]
        return column

    @staticmethod
    def escape_column(column: str) -> str:
        """
        Add escape characters if:
          - already contains stray backticks (but isn’t fully wrapped), or
          - contains more than one dot segment.
        Otherwise leave it unchanged.
        """
        # 1) already properly escaped?
        if column.startswith("`") and column.endswith("`"):
            return column

        # 2) contains >1 dots? wrap
        if column.count(".") > 1:
            return f"`{column}`"

        # 3) contains any stray backtick? strip and wrap
        if "`" in column:
            inner = column.strip("`")
            return f"`{inner}`"

        # 4) otherwise no change
        return column
