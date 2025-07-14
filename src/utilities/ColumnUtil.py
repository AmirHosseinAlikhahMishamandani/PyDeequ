# -----------------------------------------------------------------------------
# PyDeequPlus — 100% Python port of Amazon Deequ
# Author: AMIR HOSSEIN ALIKHAH MISHAMANDANI
# Email: amirhosseinalikhahm@gatech.edu
# Created: 2025-07-14
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
        else:
            return column

    @staticmethod
    def escape_column(column: str) -> str:
        """Add escape characters to column name if it contains a dot."""
        if "." in column:
            return "`" + column + "`"
        else:
            return column
