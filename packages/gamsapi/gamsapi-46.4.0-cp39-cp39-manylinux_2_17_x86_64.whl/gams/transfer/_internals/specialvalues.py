#
# GAMS - General Algebraic Modeling System Python API
#
# Copyright (c) 2017-2024 GAMS Development Corp. <support@gams.com>
# Copyright (c) 2017-2024 GAMS Software GmbH <support@gams.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import struct
import numpy as np
import pandas as pd
from typing import Union


class SpecialValues:
    NA = struct.unpack(">d", bytes.fromhex("fffffffffffffffe"))[0]
    EPS = -0.0
    UNDEF = float("nan")
    POSINF = float("inf")
    NEGINF = float("-inf")

    def isEps(records: Union[int, float, str, pd.Series, pd.DataFrame]) -> bool:
        """
        Check if the input records represent a value close to zero with specific considerations for different data types.

        Parameters
        ----------
        records: int | float | str | pd.Series | pd.DataFrame | array-like
            The input records to be checked for proximity to zero.

        Returns
        -------
        bool
            True if the input records represent a value close to zero according to the specified conditions, False otherwise.

        Raises
        ------
        Exception
            If the input (string) records cannot be converted to a float.
        Exception
            If the data structure passed in 'records' could not be converted to a numpy array (dtype=float) for testing.
        """
        if isinstance(records, (int, float)):
            records = float(records)
            return (records == 0) & (np.copysign(1, records) == -1)

        elif isinstance(records, str):
            try:
                records = float(records)
                return (records == 0) & (np.copysign(1, records) == -1)
            except Exception as err:
                raise Exception(
                    f"Attempted to convert unrecognized string `{records}` to float."
                )

        elif isinstance(records, (pd.Series, pd.DataFrame)):
            records = records.to_numpy(dtype=float)
            return (records == 0) & (np.copysign(np.ones(records.shape), records) == -1)

        else:
            try:
                records = np.array(records, dtype=float)
                return (records == 0) & (
                    np.copysign(np.ones(records.shape), records) == -1
                )
            except Exception as err:
                raise Exception(
                    "Data structure passed in 'records' could not be "
                    "converted to a numpy array (dtype=float) "
                    f"to test for GAMS EPS, reason: {err}"
                )

    def isNA(records: Union[int, float, str, pd.Series, pd.DataFrame]) -> bool:
        """
        Check if values in records represent GAMS NA (Not Available) values.

        Parameters
        ----------
        records: int | float | str | pd.Series | pd.DataFrame | array-like
            The input records to be checked for GAMS NA values.

        Returns
        -------
        bool
            True if the values in records represent GAMS NA values; otherwise, False.

        Raises
        ------
        Exception
            If the input (string) records cannot be converted to a float.
        Exception
            If the data structure passed in 'records' could not be converted to a numpy array (dtype=float) for testing.
        """
        get_bytes = lambda x: bytes(struct.pack(">d", x)).hex()
        bytr = np.vectorize(get_bytes, otypes=[np.ndarray])

        if isinstance(records, (int, float)):
            records = float(records)
            return (np.isnan(records)) & (
                bytes(struct.pack(">d", records)).hex() == "fffffffffffffffe"
            )

        elif isinstance(records, str):
            try:
                records = float(records)
                return (np.isnan(records)) & (
                    bytes(struct.pack(">d", records)).hex() == "fffffffffffffffe"
                )
            except Exception as err:
                raise Exception(
                    f"Attempted to convert unrecognized string `{records}` to float."
                )

        elif isinstance(records, (pd.Series, pd.DataFrame)):
            records = records.to_numpy(dtype=float)
            byt = bytr(records)
            return (np.isnan(records)) & (byt == "fffffffffffffffe")

        else:
            try:
                records = np.array(records, dtype=float)
                byt = bytr(records)
                return (np.isnan(records)) & (byt == "fffffffffffffffe")
            except Exception as err:
                raise Exception(
                    "Data structure passed in 'records' could not be "
                    "converted to a numpy array (dtype=float) "
                    f"to test for GAMS NA, reason: {err}"
                )

    def isUndef(records: Union[int, float, str, pd.Series, pd.DataFrame]) -> bool:
        """
        Determine if the given input(s) represent GAMS "undef" values.

        Parameters
        ----------
        records: int | float | str | pd.Series | pd.DataFrame | array-like
            The input records to be checked for GAMS "undef" values.

        Returns
        -------
        bool
            True if the values in records represent GAMS "undef" values; otherwise, False.

        Raises
        ------
        Exception
            If the input (string) records cannot be converted to a float.
        Exception
            If the data structure passed in 'records' could not be converted to a numpy array (dtype=float) for testing.
        """
        get_bytes = lambda x: bytes(struct.pack(">d", x)).hex()
        bytr = np.vectorize(get_bytes, otypes=[np.ndarray])

        if isinstance(records, (int, float)):
            records = float(records)
            return (np.isnan(records)) & (
                bytes(struct.pack(">d", records)).hex() != "fffffffffffffffe"
            )

        elif isinstance(records, str):
            try:
                records = float(records)
                return (np.isnan(records)) & (
                    bytes(struct.pack(">d", records)).hex() != "fffffffffffffffe"
                )
            except Exception as err:
                raise Exception(
                    f"Attempted to convert unrecognized string `{records}` to float."
                )

        elif isinstance(records, (pd.Series, pd.DataFrame)):
            records = records.to_numpy(dtype=float)
            byt = bytr(records)
            return (np.isnan(records)) & (byt != "fffffffffffffffe")

        else:
            try:
                records = np.array(records, dtype=float)
                byt = bytr(records)
                return (np.isnan(records)) & (byt != "fffffffffffffffe")
            except Exception as err:
                raise Exception(
                    "Data structure passed in 'records' could not be "
                    "converted to a numpy array (dtype=float) "
                    f"to test for GAMS UNDEF, reason: {err}"
                )

    def isPosInf(records: Union[int, float, str, pd.Series, pd.DataFrame]) -> bool:
        """
        Check if the input records represent positive infinity.

        Parameters
        ----------
        records: int | float | str | pd.Series | pd.DataFrame | array-like
            The input records to be checked for positive infinity values.

        Returns
        -------
        bool
            True if the values in records represent positive infinity values; otherwise, False.

        Raises
        ------
        Exception
            If the input (string) records cannot be converted to a float.
        Exception
            If the data structure passed in 'records' could not be converted to a numpy array (dtype=float) for testing.
        """
        if isinstance(records, (int, float)):
            records = float(records)
            return records == float("inf")

        elif isinstance(records, str):
            try:
                records = float(records)
                return records == float("inf")
            except Exception as err:
                raise Exception(
                    f"Attempted to convert unrecognized string `{records}` to float."
                )

        elif isinstance(records, (pd.Series, pd.DataFrame)):
            records = records.to_numpy(dtype=float)
            return np.isposinf(records)

        else:
            try:
                records = np.array(records, dtype=float)
                return np.isposinf(records)
            except Exception as err:
                raise Exception(
                    "Data structure passed in 'records' could not be "
                    "converted to a numpy array (dtype=float) "
                    f"to test for GAMS POSINF, reason: {err}"
                )

    def isNegInf(records: Union[int, float, str, pd.Series, pd.DataFrame]) -> bool:
        """
        Check if the input records represent negative infinity.

        Parameters
        ----------
        records: int | float | str | pd.Series | pd.DataFrame | array-like
            The input records to be checked for negative infinity values.

        Returns
        -------
        bool
            True if the values in records represent negative infinity values; otherwise, False.

        Raises
        ------
        Exception
            If the input (string) records cannot be converted to a float.
        Exception
            If the data structure passed in 'records' could not be converted to a numpy array (dtype=float) for testing.
        """
        if isinstance(records, (int, float)):
            records = float(records)
            return records == float("-inf")

        elif isinstance(records, str):
            try:
                records = float(records)
                return records == float("inf")
            except Exception as err:
                raise Exception(
                    f"Attempted to convert unrecognized string `{records}` to float."
                )

        elif isinstance(records, (pd.Series, pd.DataFrame)):
            records = records.to_numpy(dtype=float)
            return np.isneginf(records)

        else:
            try:
                records = np.array(records, dtype=float)
                return np.isneginf(records)
            except Exception as err:
                raise Exception(
                    "Data structure passed in 'records' could not be "
                    "converted to a numpy array (dtype=float) "
                    f"to test for GAMS NEGINF, reason: {err}"
                )
