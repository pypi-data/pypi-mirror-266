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

from copy import copy
import os
import sys
import datetime
import gams.transfer as gt
import openpyxl
from openpyxl.utils.cell import (
    coordinate_from_string,
    column_index_from_string,
)
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pandas as pd
import numpy as np
from gams.core.gdx import GMS_SV_UNDEF
from gams.transfer.syms._methods.tables import (
    _assert_axes_no_nans,
    _get_implied_dimension_from_axes,
    _flatten_and_convert,
)
from gams.connect.agents.connectagent import ConnectAgent
from cerberus import Validator


class ExcelReader(ConnectAgent):
    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        self._parse_options()

        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)
            np.set_printoptions(threshold=sys.maxsize)
        if os.path.splitext(self._file)[1] in [".xls"]:
            self.connect_error("The ExcelReader does not support .xls files.")

    def _parse_options(self):
        self._file = self._inst["file"]
        self._cdim = self._inst.get("columnDimension", 1)
        self._rdim = self._inst.get("rowDimension", 1)
        self._sym_type = self._inst.get("type", "par")
        self._merged_cells = self._inst.get("mergedCells", False)
        self._skip_empty = self._inst.get("skipEmpty", 1)
        self._value_subs = self._inst.get("valueSubstitutions", None)
        self._index_subs = self._inst.get("indexSubstitutions", None)
        self._index = self._inst.get("index", None)
        self._auto_merge = self._inst.get("autoMerge", False)
        self._ignore_text = self._inst.get("ignoreText", "auto")
        self._trace = self._inst.get("trace", self._cdb.options.get("trace", 0))

        if self._trace > 1:
            self._cdb.print_log(
                "Input (root):"
                f"\n  file: >{self._inst['file']}<"
                f"\n  rowDimension: >{self._inst.get('rowDimension', '')}<"
                f"\n  columnDimension: >{self._inst.get('columnDimension', '')}<"
                f"\n  type: >{self._inst.get('type', '')}<"
                f"\n  mergedCells: >{self._inst.get('mergedCells', '')}<"
                f"\n  skipEmpty: >{self._inst.get('skipEmpty', '')}<"
                f"\n  valueSubstitutions: >{self._inst.get('valueSubstitutions', '')}<"
                f"\n  indexSubstitutions: >{self._inst.get('indexSubstitutions', '')}<"
                f"\n  index: >{self._inst.get('index', '')}<"
                f"\n  autoMerge: >{self._inst.get('autoMerge', '')}<"
                f"\n  ignoreText: >{self._inst.get('ignoreText', '')}<"
                f"\n  trace: >{self._inst.get('trace', '')}<"
                "\n"
            )

        self._file = os.path.abspath(self._file)

        if self._trace > 1:
            self._cdb.print_log(
                "Processed Input (root):"
                f"\n  file: >{self._file}<"
                f"\n  rowDimension: >{self._rdim}<"
                f"\n  columnDimension: >{self._cdim}<"
                f"\n  type: >{self._sym_type}<"
                f"\n  mergedCells: >{self._merged_cells}<"
                f"\n  skipEmpty: >{self._skip_empty}<"
                f"\n  valueSubstitutions: >{self._value_subs}<"
                f"\n  indexSubstitutions: >{self._index_subs}<"
                f"\n  index: >{self._index}<"
                f"\n  autoMerge: >{self._auto_merge}<"
                f"\n  ignoreText: >{self._ignore_text}<"
                f"\n  trace: >{self._trace}<"
                "\n"
            )

    def _apply_skip_empty(self, dim, idx, skip_empty):
        stop = None
        count = 0
        if dim > 0 and skip_empty > -1:
            for i in range(idx.shape[1]):
                if (np.array(idx[:, i] == None)).all():
                    count += 1
                else:
                    count = 0
                if count > skip_empty:
                    stop = i - skip_empty
                    break
        return stop

    def _create_index(self, dim, idx):
        if dim > 1:
            return pd.MultiIndex.from_arrays(idx)
        else:
            return idx.flatten()

    def _remove_missing_index(self, values, rdim, cdim, row_idx, col_idx, method):
        def _keep_list(idx):
            keep = list(range(idx.shape[1]))
            for i in reversed(range(idx.shape[1])):
                if method(v is None for v in idx[:, i]):
                    del keep[i]
            return keep

        if rdim > 0:
            keep = _keep_list(row_idx)
            row_idx = row_idx[:, keep]
            values = values[keep]

        if cdim > 0:
            keep = _keep_list(col_idx)
            col_idx = col_idx[:, keep]
            values = values[:, keep]

        return values, row_idx, col_idx

    def _apply_auto_merge(self, idx, dim):
        last_label = [None] * dim
        for i in range(idx.shape[1]):
            if any(idx[:, i] != None):
                for j in range(idx.shape[0]):
                    if idx[j, i] is None:
                        idx[j, i] = last_label[j]
                last_label = idx[:, i]
        return idx

    def _create_dataframe(self, col_idx, row_idx, values, rdim, cdim):
        # create column and row index used for DataFrame
        col_idx = self._create_index(cdim, col_idx)
        row_idx = self._create_index(rdim, row_idx)

        if cdim == rdim == 0:
            df = pd.DataFrame(values.flatten())
        elif cdim == 0:
            values = values[:, 0]
            df = pd.DataFrame(values.flatten(), index=row_idx)
        elif rdim == 0:
            values = values[0, :]
            df = pd.DataFrame(values.flatten(), index=col_idx)
        else:
            df = pd.DataFrame(values, index=row_idx, columns=col_idx)
        return df

    def _parse_range(self, sym_range):
        def coords_to_row_col(coordinates):
            c = coordinate_from_string(coordinates)
            return c[1], column_index_from_string(c[0])

        if "!" not in sym_range:  # named range
            if sym_range not in self._wb.defined_names:
                self.connect_error(f"Named range >{sym_range}< does not exist.")
            rng = list(self._wb.defined_names[sym_range].destinations)
            if len(rng) > 1:
                self.connect_error(
                    f"Named range is not contiguous: {sym_range} -> {rng}"
                )
            rng = rng[0]
            resolved_range = "!".join(rng)
            sym_range = resolved_range
        elif sym_range.endswith("!"):  # sheet specified but range missing
            sym_range += "A1"

        sheet, rng = sym_range.split("!")
        sheet = sheet.lower()
        sheet_names = [n.lower() for n in self._wb.sheetnames]
        if sheet not in sheet_names:
            self.connect_error(f"Sheet >{sheet}< not found.")
        sheet = self._wb.worksheets[sheet_names.index(sheet)]
        nw, se = rng.split(":") if ":" in rng else (rng, None)

        nw_row, nw_col = coords_to_row_col(nw)
        se_col = se_row = None
        if se is not None:
            se_row, se_col = coords_to_row_col(se)

        return sheet, nw_col - 1, nw_row - 1, se_col, se_row

    def _resolve_merged_cells(self, sheet, data):
        # TODO: do this only on the used range for better performance
        for mr in sheet.merged_cells.ranges:
            nwc, nwr, sec, ser = mr.bounds
            value = data[nwr - 1][nwc - 1]
            data[nwr - 1 : ser, nwc - 1 : sec] = value
        return data

    def _convert_dates(self, df):
        for col in df.columns:
            if is_datetime(df[col]):
                df[col] = (
                    pd.DatetimeIndex(df[col]).to_julian_date()
                    - pd.Timestamp("1899-12-30").to_julian_date()
                )

        has_datetime = any(
            isinstance(x, datetime.datetime) for x in df.values.flatten()
        )
        if has_datetime:
            if hasattr(pd.DataFrame, "map"):
                df = df.map(
                    lambda x: (
                        pd.Timestamp(x).to_julian_date()
                        - pd.Timestamp("1899-12-30").to_julian_date()
                        if isinstance(x, datetime.datetime)
                        else x
                    )
                )
            else:
                df = df.applymap(
                    lambda x: (
                        pd.Timestamp(x).to_julian_date()
                        - pd.Timestamp("1899-12-30").to_julian_date()
                        if isinstance(x, datetime.datetime)
                        else x
                    )
                )

        return df

    def _index_substitutions(self, row_idx, col_idx, rdim, cdim, index_subs):
        if index_subs and rdim + cdim > 0:
            subs = copy(index_subs)
            for k, v in subs.items():
                if k is None:
                    break
                if k != k:  # check for float('nan')
                    if None not in subs.keys():
                        subs[None] = v
                    break
            if rdim > 0:
                ri_tmp = copy(row_idx)
                for k, v in subs.items():
                    # change value in array if either row_idx==k or (element is .nan (row_idx!=row_idx) and key is .nan (k!=k))
                    ri_tmp[
                        np.logical_or(
                            row_idx == k, np.logical_and(row_idx != row_idx, k != k)
                        )
                    ] = v
                row_idx = ri_tmp
            if cdim > 0:
                ci_tmp = copy(col_idx)
                for k, v in subs.items():
                    # change value in array if either col_idx==k or (element is .nan (col_idx!=col_idx) and key is .nan (k!=k))
                    ci_tmp[
                        np.logical_or(
                            col_idx == k, np.logical_and(col_idx != col_idx, k != k)
                        )
                    ] = v
                col_idx = ci_tmp
        return row_idx, col_idx
        # alternative approach, but much slower
        # vectorized_replace_rows = np.vectorize(lambda v: dict().get(v, v), otypes=[row_idx.dtype])
        # vectorized_replace_cols = np.vectorize(lambda v: dict().get(v, v), otypes=[col_idx.dtype])
        #
        # if rdim > 0:
        #    row_idx = vectorized_replace_rows(row_idx)
        # if cdim > 0:
        #    col_idx = vectorized_replace_cols(col_idx)

    def _value_substitutions(self, df, value_sub):
        if value_sub is not None:
            df.replace(value_sub, inplace=True)
        return df

    def _write(self, df, sym_name, sym_type, rdim, cdim):
        if df.empty or df.isnull().all().all():
            df = None
        # pass DataFrame as Series for rdim=0 or cdim=0 to not confuse gams.transfer with dimensions
        elif (cdim == 0 and rdim != 0) or (rdim == 0 and cdim != 0):
            df = df[0]

        if sym_type == "par":
            sym = self._cdb._container.addParameter(
                sym_name,
                ["*"] * (rdim + cdim),
                records=df,
                uels_on_axes=True,
            )
            if df is not None:
                sym.dropUndef()  # drop float('nan')
                # TODO: remove this section as soon as gams.transfer supports dropping NaN values
                self._value_substitutions(
                    sym.records, {GMS_SV_UNDEF: gt.SpecialValues.UNDEF}
                )

        else:  # set
            if df is not None:
                # TODO: remove this section as soon as gams.transfer supports dropping NaN values
                # Nan values become empty set element text and we can not drope those values after they are in the container.
                # This is the workaround to handle this
                _assert_axes_no_nans(df)
                dim = _get_implied_dimension_from_axes(df)
                if dim != rdim + cdim:
                    self.connect_error(
                        f"Dimensionality of table ({dim}) is inconsistent with set domain specification ({rdim+cdim})"
                    )
                df = _flatten_and_convert(df)
                df.dropna(inplace=True)
            sym = self._cdb._container.addSet(
                sym_name,
                ["*"] * (rdim + cdim),
                records=df,
                uels_on_axes=False,
            )

    def _ignore_rows(self, data, offset, ignore_rows):
        nr_rows = data.shape[0]
        r = list(
            filter(
                lambda x: x + offset + 1 not in ignore_rows,
                range(nr_rows),
            )
        )
        data = data[r]
        return data

    def _ignore_columns(self, data, offset, ignore_columns):
        nr_cols = data.shape[1]
        r = list(
            filter(
                lambda x: x + offset + 1 not in ignore_columns,
                range(nr_cols),
            )
        )
        data = data[:, r]
        return data

    def _apply_ignore_rows_columns(
        self, data, ignore_rows, ignore_columns, nw_row, nw_col, sym_name
    ):
        # apply ignoreRows
        if ignore_rows is not None:
            data = self._ignore_rows(data, nw_row, ignore_rows)
            if self._trace > 2:
                self._cdb.print_log(
                    f"Raw data after ignoreRows ({sym_name}):\n{data}\n"
                )

        # apply ignoreColumns
        if ignore_columns is not None:
            data = self._ignore_columns(data, nw_col, ignore_columns)
            if self._trace > 2:
                self._cdb.print_log(
                    f"Raw data after ignoreColumns ({sym_name}):\n{data}\n"
                )
        return data

    def _parse_ignore_rows(self, ignore_rows, nw_row, se_row):
        if ignore_rows is None:
            return []
        if isinstance(ignore_rows, int):
            l = [ignore_rows]
        else:
            l = ignore_rows
        l = set(l)
        if se_row is None:
            return list(l)
        l = list(filter(lambda x: x >= nw_row and x <= se_row, l))
        return l

    def _parse_ignore_columns(self, ignore_columns, nw_col, se_col):
        if ignore_columns is None:
            return []
        if isinstance(ignore_columns, int):
            l = [ignore_columns]
        elif isinstance(ignore_columns, str):
            l = [column_index_from_string(ignore_columns)]
        else:  # list
            l = []
            for c in ignore_columns:
                if isinstance(c, int):
                    l.append(c)
                else:  # string
                    l.append(column_index_from_string(c))
        l = set(l)
        if se_col is None:
            return list(l)
        l = list(filter(lambda x: x >= nw_col and x <= se_col, l))
        return l

    def _read_symbol(self, sym):
        if self._trace > 1:
            self._cdb.print_log(
                "Input (symbol):"
                f"\n  name: >{sym.get('name', '')}<"
                f"\n  range: >{sym.get('range', '')}<"
                f"\n  rowDimension: >{sym.get('rowDimension', '')}<"
                f"\n  columnDimension: >{sym.get('columnDimension', '')}<"
                f"\n  type: >{sym.get('type', '')}<"
                f"\n  mergedCells: >{sym.get('mergedCells', '')}<"
                f"\n  valueSubstitutions: >{sym.get('valueSubstitutions', '')}<"
                f"\n  indexSubstitutions: >{sym.get('indexSubstitutions', '')}<"
                f"\n  skipEmpty: >{sym.get('skipEmpty', '')}<"
                f"\n  autoMerge: >{sym.get('autoMerge', '')}<"
                f"\n  ignoreText: >{sym.get('ignoreText', '')}<"
                f"\n  ignoreRows: >{sym.get('ignoreRows', '')}<"
                f"\n  ignoreColumns: >{sym.get('ignoreColumns', '')}<"
                "\n"
            )
        sym_name = sym["name"]
        sym_range = sym.get("range", sym_name + "!A1")
        sym_type = sym.get("type", self._sym_type)
        merged_cells = sym.get("mergedCells", self._merged_cells)
        rdim = sym.get("rowDimension", self._rdim)
        cdim = sym.get("columnDimension", self._cdim)
        value_subs = sym.get("valueSubstitutions", self._value_subs)
        index_subs = sym.get("indexSubstitutions", self._index_subs)
        skip_empty = sym.get("skipEmpty", self._skip_empty)
        auto_merge = sym.get("autoMerge", self._auto_merge)
        ignore_text = sym.get("ignoreText", self._ignore_text)

        sheet, nw_col, nw_row, se_col, se_row = self._parse_range(sym_range)
        nw_only = se_col is None and se_row is None
        ignore_rows = self._parse_ignore_rows(sym.get("ignoreRows"), nw_row, se_row)
        ignore_columns = self._parse_ignore_columns(
            sym.get("ignoreColumns"), nw_col, se_col
        )
        required_rows = cdim + 1 + len(ignore_rows)
        required_cols = rdim + 1 + len(ignore_columns)
        if not nw_only:
            nr_cols = se_col - nw_col
            nr_rows = se_row - nw_row

        # handle ignoreText=auto
        if sym_type == "set" and ignore_text == "auto":
            ignore_text = False
            if rdim == 0:
                if (
                    nw_only or nr_rows < required_rows
                ):  # nw only or range without set element text
                    ignore_text = True
            if cdim == 0:
                if (
                    nw_only or nr_cols < required_cols
                ):  # nw only or range without set element text
                    ignore_text = True

        if self._trace > 1:
            self._cdb.print_log(
                "Processed Input (symbol):"
                f"\n  name: >{sym_name}<"
                f"\n  range: >{sym_range}<"
                f"\n  rowDimension: >{rdim}<"
                f"\n  columnDimension: >{cdim}<"
                f"\n  type: >{sym_type}<"
                f"\n  mergedCells: >{merged_cells}<"
                f"\n  valueSubstitutions: >{value_subs}<"
                f"\n  indexSubstitutions: >{index_subs}<"
                f"\n  skipEmpty: >{skip_empty}<"
                f"\n  autoMerge: >{auto_merge}<"
                f"\n  ignoreText: >{ignore_text}<"
                f"\n  ignoreRows: >{ignore_rows}<"
                f"\n  ignoreColumns: >{ignore_columns}<"
                "\n"
            )

        # check that sets do not have dim=0
        if sym_type == "set" and rdim == 0 and cdim == 0:
            self.connect_error(
                f"Cannot read set >{sym_name}< with both rowDimension=0 and columnDimension=0."
            )

        # check sufficient ranges
        if sym_type == "set" and ignore_text:
            if cdim == 0:
                required_cols -= 1
            elif rdim == 0:
                required_rows -= 1
        if not nw_only:
            if sym_type == "set" and not ignore_text:
                if cdim == 0 and nr_cols == required_cols - 1:
                    self.connect_error(
                        "Range and rowDimension specification does not contain set element text but ignoreText has been set to False. Adjust range or rowDimension or set ignoreText=True."
                    )
                if rdim == 0 and nr_rows == required_rows - 1:
                    self.connect_error(
                        "Range and columnDimension specification does not contain set element text but ignoreText has been set to False. Adjust range or columnDimension or set ignoreText=True."
                    )
            if nr_rows < required_rows:
                self.connect_error(
                    f"Invalid range >{sym_range}<. With columnDimension: >{cdim}< and {len(ignore_rows)} rows to be ignored, the range must include at least {required_rows} rows."
                )
            if nr_cols < required_cols:
                self.connect_error(
                    f"Invalid range >{sym_range}<. With rowDimension: >{rdim}< and {len(ignore_columns)} columns to be ignored, the range must include at least {required_cols} columns."
                )

        data = np.array(
            list(sheet.values), dtype=object
        )  # dtype=object is required to not convert int values (e.g. 1) to float automatically (e.g. 1.0)

        if len(data) == 0:  # no data at all
            self._write(pd.DataFrame(), sym_name, sym_type, rdim, cdim)
            return

        if self._trace > 2:
            self._cdb.print_log(f"Raw data ({sym_name}) :\n{data}\n")

        if merged_cells:
            data = self._resolve_merged_cells(sheet, data)
            if self._trace > 2:
                self._cdb.print_log(
                    f"Raw data after resolving merged cells ({sym_name}):\n{data}\n"
                )

        # shrink data to actual range
        data = data[nw_row:se_row, nw_col:se_col]
        if self._trace > 2:
            self._cdb.print_log(
                f"Raw data after shrinking to range ({sym_name}):\n{data}\n"
            )

        # apply ignoreRows and ignoreColumns
        data = self._apply_ignore_rows_columns(
            data, ignore_rows, ignore_columns, nw_row, nw_col, sym_name
        )
        if len(data) == 0:
            self._write(pd.DataFrame(), sym_name, sym_type, rdim, cdim)
            return
        # if data.shape[0] < required_rows - len(ignore_rows):
        #    self.connect_error(
        #        f"Insufficient number of data rows ({sym_name}). Require at least {required_rows}, but got {data.shape[0]}."
        #    )
        # if data.shape[1] < required_cols - len(ignore_columns):
        #    self.connect_error(
        #        f"Insufficient number of data columns ({sym_name}). Require at least {required_cols}, but got {data.shape[1]}."
        #    )

        col_idx = data[:cdim, rdim:]
        row_idx = data[cdim:, :rdim].transpose()

        if self._trace > 2:
            self._cdb.print_log(f"Initial column index ({sym_name}):\n{col_idx}\n")
            self._cdb.print_log(f"Initial row index ({sym_name}):\n{row_idx}\n")

        # apply skipEmpty only for nw_only, but not for explicit ranges
        if nw_only:
            stop_col = self._apply_skip_empty(cdim, col_idx, skip_empty)
            col_idx = col_idx[:, :stop_col]
            stop_row = self._apply_skip_empty(rdim, row_idx, skip_empty)
            row_idx = row_idx[:, :stop_row]
            if self._trace > 2:
                self._cdb.print_log(
                    f"Column index after skipEmpty ({sym_name}):\n{col_idx}\n"
                )
                self._cdb.print_log(
                    f"Row index after skipEmpty ({sym_name}):\n{row_idx}\n"
                )
        else:
            stop_col = None
            stop_row = None

        if stop_col is not None:
            stop_col += rdim
        if stop_row is not None:
            stop_row += cdim

        if cdim == 0 and rdim == 0:  # handle scalars
            stop_row = 1
            stop_col = 1
        if rdim == 0:
            row_idx = np.empty((0, 0))  # dummy array for header
        if cdim == 0:
            col_idx = np.empty((0, 0))  # dummy array for header

        values = data[cdim:stop_row, rdim:stop_col]

        if self._trace > 2:
            self._cdb.print_log(f"Values {(sym_name)}: {values}\n")

        if auto_merge:
            if cdim > 1:
                col_idx = self._apply_auto_merge(col_idx, cdim)
            if rdim > 1:
                row_idx = self._apply_auto_merge(row_idx, rdim)
            if self._trace > 2:
                self._cdb.print_log(
                    f"Row index after autoMerge ({sym_name}):\n{row_idx}\n"
                )
                self._cdb.print_log(
                    f"Column index after autoMerge ({sym_name}):\n{col_idx}\n"
                )

        # replace all set text with empty string for ignoreText=True
        if sym_type == "set" and ignore_text:
            if values.size == 0:
                if cdim == 0:
                    values = np.empty((values.shape[0], 1), dtype=str)
                elif rdim == 0:
                    values = np.empty((1, values.shape[1]), dtype=str)
            else:
                values = np.empty_like(values, dtype=str)

        if index_subs:
            # remove all-None entries in column and row header and corresponding values
            values, row_idx, col_idx = self._remove_missing_index(
                values, rdim, cdim, row_idx, col_idx, all
            )

            row_idx, col_idx = self._index_substitutions(
                row_idx, col_idx, rdim, cdim, index_subs
            )
            if self._trace > 2:
                self._cdb.print_log(
                    f"Row index after indexSubstitutions ({sym_name}):\n{row_idx}\n"
                )
                self._cdb.print_log(
                    f"Column index after indexSubstitutions ({sym_name}):\n{col_idx}\n"
                )

        # remove any-None entries in column and row header and corresponding values
        values, row_idx, col_idx = self._remove_missing_index(
            values, rdim, cdim, row_idx, col_idx, any
        )

        if self._trace > 2:
            self._cdb.print_log(
                f"Column index before DataFrame creation ({sym_name}):\n{col_idx}\n"
            )
            self._cdb.print_log(
                f"Row index before DataFrame creation ({sym_name}):\n{row_idx}\n"
            )
            self._cdb.print_log(
                f"Values before DataFrame creation ({sym_name}):\n{values}\n"
            )

        df = self._create_dataframe(col_idx, row_idx, values, rdim, cdim)

        if self._trace > 2:
            self._cdb.print_log(f"Initial DataFrame ({sym_name}):\n{df}\n")

        df = self._convert_dates(df)

        df = self._value_substitutions(df, value_subs)
        if self._trace > 2:
            self._cdb.print_log(
                f"DataFrame after valueSubstitutions ({sym_name}):\n{df}\n"
            )

        # TODO: This is a workaround to get UNDEF to survive sym.dropNA/sym.dropUndef - remove as soon as gams.transfer supports dropping NaN values
        if sym_type == "par":
            import re

            pattern = re.compile(r"undef", re.IGNORECASE)
            df.replace(regex=pattern, value=GMS_SV_UNDEF, inplace=True)
        self._write(df, sym_name, sym_type, rdim, cdim)

    def open(self):
        read_only = not (
            any(
                sym.get("mergedCells", self._merged_cells)
                for sym in self._inst.get("symbols", [])
            )
            or self._merged_cells
        )
        self._wb = openpyxl.load_workbook(
            self._file, read_only=read_only, data_only=True
        )  # data_only=True is required to read values instead of formulas

    def _read_from_index(self):
        def key_map(key):
            if key is None:
                return None
            key = key.lower().strip()
            if key in ["rdim", "rowdimension"]:
                return "rowDimension"
            if key in ["cdim", "columndimension"]:
                return "columnDimension"
            if key in ["skipempty", "se"]:
                return "skipEmpty"
            if key in ["ignoretext"]:
                return "ignoreText"
            if key in ["automerge"]:
                return "autoMerge"
            if key in ["ignorerows"]:
                return "ignoreRows"
            if key in ["ignorecolumns"]:
                return "ignoreColumns"
            if key in ["mergedcells"]:
                return "mergedCells"
            if self._trace > 0 and key != "":
                self._cdb.print_log(f"  Ignoring unsupported parameter {key}.")
            return ""

        def value_map(key, value):
            if isinstance(value, str):
                value = value.strip()
            m = {}
            m["autoMerge"] = {
                1: True,
                True: True,
                "true": True,
                "1": True,
                0: False,
                False: False,
                "false": False,
                "0": False,
            }
            m["ignoreText"] = {**m["autoMerge"], **{"auto": "auto"}}
            m["mergedCells"] = m["autoMerge"]
            if key in ["autoMerge", "ignoreText", "mergedCells"]:
                if isinstance(value, str):
                    value = value.lower()
                v = m[key].get(value, None)
                if v is None:
                    self.connect_error(
                        f"Invalid value >{value}< for {key}. Allowed values are {', '.join(m[key].keys())}."
                    )
            elif key == "ignoreRows":
                if isinstance(value, str):
                    l = value.split(",")
                    l = [x.strip() for x in l]
                    if any(not x.isnumeric() for x in l):
                        self.connect_error("Values for ignoreRows need to be numeric.")
                    v = [int(x) for x in l]
                else:
                    v = [value]
            elif key == "ignoreColumns":
                if isinstance(value, str):
                    l = value.split(",")
                    l = [x.strip() for x in l]
                    v = []
                    for x in l:
                        if x.isnumeric():
                            v.append(int(x))
                        else:
                            v.append(column_index_from_string(x))
                else:
                    v = [value]
            elif isinstance(value, str) and value.isnumeric():
                v = int(value)
            else:
                v = value
            return v

        def parse_key_value(value):
            args = value
            args = args.replace("=", " ")
            args = args.split(" ")
            args = list(filter(lambda x: x != " ", args))
            ret = {}
            for args_idx in range(0, len(args), 2):
                key = args[args_idx].strip()
                key = key_map(key)
                if key is not None and len(key) != 0:
                    value = args[args_idx + 1].strip()
                    if value is not None:
                        value = value_map(key, value)
                        ret[key] = value
            return ret

        sheet, nw_col, nw_row, se_col, se_row = self._parse_range(self._index)
        data = np.array(list(sheet.values), dtype=object)
        data = data[nw_row:se_row, nw_col:se_col]
        header = data[0]
        for idx, h in enumerate(header):
            header[idx] = key_map(h)

        symbols = []
        global_par = {}
        is_symbol = False
        for rec in data[1:]:
            if None in (rec[0], rec[1], rec[2]):
                is_symbol = False
            else:
                is_symbol = True
                local_par = {}
                local_par["type"] = rec[0].lower().strip()
                local_par["name"] = rec[1].strip()
                local_par["range"] = rec[2].strip()
                if self._trace > 2:
                    self._cdb.print_log(
                        f"\nIndex sheet: Parse symbol >{local_par['name']}< with type=>{local_par['type']}< and range=>{local_par['range']}<."
                    )
            for idx, h in enumerate(header[3:]):
                key = key_map(h)
                value = rec[idx + 3]
                if isinstance(value, str):
                    value = value.strip()
                params = {}
                if key is None:  # parse arbitrary key-value pairs
                    if value is not None:
                        params = parse_key_value(value)
                elif len(key) == 0:
                    continue
                elif value is not None:
                    params = {key: value_map(key, value)}

                for k, v in params.items():
                    if is_symbol:
                        if self._trace > 2:
                            self._cdb.print_log(
                                f"  Add parameter {k}={v} to symbol >{local_par['name']}<."
                            )
                        local_par[k] = v
                    else:
                        if self._trace > 2:
                            self._cdb.print_log(
                                f"  Add parameter {k}={v} to root parameters."
                            )
                        global_par[k] = v

            if is_symbol:
                sym = global_par.copy()
                sym.update(local_par)
                sym["rowDimension"] = sym.get("rowDimension", 0)
                sym["columnDimension"] = sym.get("columnDimension", 0)
                symbols.append(sym)

        # reopen the file with read_only=False if required
        if not self._merged_cells:
            read_only = not any(
                sym.get("mergedCells", self._merged_cells) for sym in symbols
            )
            if not read_only:
                self._wb.close()
                self._wb = openpyxl.load_workbook(
                    self._file, read_only=read_only, data_only=True
                )  # data_only=True is required to read values instead of formulas
        for i, sym in enumerate(symbols):
            sym_schema = self.cerberus()["symbols"]["schema"]["schema"]
            v = Validator(sym_schema)
            if not v.validate(sym):
                self.connect_error(
                    f"Validation of item {i} in index failed: {v.errors}"
                )
            self._read_symbol(sym)

    def execute(self):
        if self._index:
            self._read_from_index()
        else:
            for sym in self._inst["symbols"]:
                self._read_symbol(sym)
        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            for name, sym in self._cdb._container.data.items():
                self._cdb.print_log(
                    f"Connect Container symbol >{name}<:\n {sym.records}\n"
                )

    def close(self):
        self._wb.close()
