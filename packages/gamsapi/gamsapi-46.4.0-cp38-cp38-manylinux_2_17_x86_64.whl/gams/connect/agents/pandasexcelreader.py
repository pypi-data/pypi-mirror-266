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

import datetime
import openpyxl
import os
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pandas as pd
import numpy as np
from gams import transfer as gt
from gams.connect.agents.connectagent import ConnectAgent


class PandasExcelReader(ConnectAgent):

    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        self._cdb.print_log(
            "Warning: PandasExcelReader is deprecated and will be removed in a future release. Use ExcelReader instead."
        )
        self._file = os.path.abspath(self._inst["file"])
        self._cdim = inst.get("columnDimension", 1)
        self._rdim = inst.get("rowDimension", 1)
        self._multicolumnblankrow = inst.get("multiColumnBlankRow", True)
        self._sym_type = inst.get("type", "par")
        self._trace = inst.get("trace", cdb.options.get("trace", 0))
        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)
        if (
            os.path.splitext(self._file)[1] not in [".xls", ".xlsx", ".xlsm"]
            and self._trace > 0
        ):
            self._cdb.print_log(
                f"Warning: Other file extensions than .xls, .xlsx and .xlsm may require installing additional Python packages. Please refer to the documentation of the PandasExcelReader agent for more information."
            )

    def open(self):
        if self._trace > 1:
            self._cdb.print_log(
                f'Input (global): file: >{self._inst["file"]}< rowDimension: >{self._inst.get("rowDimension", "")}< columnDimension: >{self._inst.get("columnDimension", "")}< type: >{self._inst.get("type", "")}< trace: >{self._inst.get("trace", "")}< excelFileArguments: >{self._inst.get("excelFileArguments", "")}<\n'
            )
        if self._trace > 1:
            self._cdb.print_log(
                f'Processed Input (global): file: >{self._file}< rowDimension: >{self._rdim}< columnDimension: >{self._cdim}< type: >{self._sym_type}< excelFileArguments: >{self._inst.get("excelFileArguments", "")}< trace: >{self._trace}<\n'
            )
        self._excel_file = pd.ExcelFile(
            self._file, **self._inst.get("excelFileArguments", {})
        )

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

    def _read_excel(
        self,
        sym_name,
        sym_type,
        rdim,
        cdim,
        multicolumnblankrow,
        sheet,
        startrow,
        startcol,
        endrow,
        endcol,
        read_excel_args=None,
        value_sub=None,
        drop=None,
    ):
        if read_excel_args is None:
            read_excel_args = {}
        dim = rdim + cdim
        if endrow is None and rdim == 0:
            if cdim > 1:
                endrow = startrow + cdim + 1
                if not multicolumnblankrow:
                    endrow = endrow - 1
            else:
                endrow = startrow + 1
        if endcol is None and cdim == 0:
            endcol = startcol + max(1, rdim)
        nrows = None
        if endrow is not None:
            nrows = endrow - startrow - max(0, cdim - 1)
            if self._trace > 1:
                self._cdb.print_log(f"nrows: {nrows}\n")
        if dim == 0:
            kwargs = {
                "sheet_name": sheet,
                "nrows": nrows,
                "skiprows": startrow,
                "index_col": startcol,
            }
            kwargs.update(read_excel_args)
        elif rdim == dim:
            kwargs = {
                "sheet_name": sheet,
                "nrows": nrows,
                "skiprows": startrow,
                "index_col": list(range(startcol, rdim + startcol)),
            }
            kwargs.update(read_excel_args)
        elif rdim == 0:
            if dim == 1:
                kwargs = {
                    "sheet_name": sheet,
                    "nrows": nrows,
                    "header": [startrow],
                    "index_col": startcol,
                }
                kwargs.update(read_excel_args)
            else:
                kwargs = {
                    "sheet_name": sheet,
                    "nrows": nrows,
                    "header": list(range(startrow, cdim + startrow)),
                    "index_col": [startcol],
                }
                kwargs.update(read_excel_args)
        else:
            kwargs = {
                "sheet_name": sheet,
                "nrows": nrows,
                "header": list(range(startrow, cdim + startrow)),
                "index_col": list(range(startcol, rdim + startcol)),
            }
            kwargs.update(read_excel_args)

        df = pd.read_excel(self._excel_file, **kwargs)
        if self._trace > 2:
            self._cdb.print_log(f"DataFrame({sym_name}) after pd.read_excel:\n{df}\n")

        if endcol:
            endcol = endcol - max(0, rdim - 1)

        if self._trace > 1:
            self._cdb.print_log(
                f"Cropping startcol: <{startcol}> to endcol: <{endcol}>\n"
            )
        df = df.iloc[:, startcol:endcol]  # drop unnamed columns
        if self._trace > 2:
            self._cdb.print_log(
                f"DataFrame({sym_name}) after cropping columns:\n{df}\n"
            )

        if cdim > 1:
            index0 = df.index[0]
            if type(index0) == float and np.isnan(index0):  # drop first row
                df.drop(df.head(1).index, inplace=True)
            elif (
                not nrows is None and len(df.index) == nrows and multicolumnblankrow
            ):  # drop last row because we read one row too many
                df.drop(df.tail(1).index, inplace=True)
            if self._trace > 2:
                self._cdb.print_log(
                    f"DataFrame({sym_name}) after potentially dropping rows:\n{df}\n"
                )

        df = self._convert_dates(df)

        # write relaxed domain information
        if dim == 0:
            domain = []
        elif rdim == 0:
            domain = [str(d) if d is not None else "*" for d in df.columns.names]
        elif cdim == 0:
            domain = [str(d) if d is not None else "*" for d in df.index.names]
        else:
            domain = [
                str(d) if d is not None else "*"
                for d in df.index.names + df.columns.names
            ]

        columns = None
        if dim > 0:
            if rdim == dim:
                df.reset_index(drop=False, inplace=True)
            elif rdim == 0:
                columns = df.columns
                indices = df.index
                df = pd.melt(df)
            else:
                columns = df.columns
                indices = df.index
                df = pd.melt(df, ignore_index=False)
                df.reset_index(drop=False, inplace=True)

        if self._trace > 2:
            self._cdb.print_log(f"DataFrame({sym_name}) after melt:\n{df}\n")

        if drop:
            df.iloc[:, :-1] = df.iloc[:, :-1].astype(str)
            for col in df.columns[:-1]:
                df = df[~df[col].str.contains(drop, na=False)]
            if self._trace > 2:
                self._cdb.print_log(
                    f"DataFrame({sym_name}) after processing <drop>:\n{df}\n"
                )

        if value_sub:
            df.iloc[:, -1].replace(value_sub, inplace=True)
            if self._trace > 2:
                self._cdb.print_log(
                    f"DataFrame({sym_name}) after processing <valueSubstitutions>:\n{df}\n"
                )

        df = df.dropna()

        if sym_type == "par":
            sym = gt.Parameter(self._cdb._container, sym_name, domain=domain)
        elif sym_type == "set":
            sym = gt.Set(self._cdb._container, sym_name, domain=domain)
            df.iloc[:, -1] = df.iloc[:, -1].astype(str)

        if self._trace > 2:
            self._cdb.print_log(
                f"Final DataFrame({sym_name}) that will be processed by GAMSTransfer:\n{df}"
            )

        if not df.empty:
            sym.setRecords(df)

        if sym.records is not None and columns is not None:
            for i in range(rdim):
                if hasattr(pd.DataFrame, "isetitem"):
                    sym.records.isetitem(
                        i,
                        sym.records.iloc[:, i].astype(
                            pd.CategoricalDtype(
                                categories=indices.get_level_values(i)
                                .map(str)
                                .map(str.rstrip)
                                .unique(),
                                ordered=True,
                            )
                        ),
                    )
                else:
                    sym.records.iloc[:, i] = sym.records.iloc[:, i].astype(
                        pd.CategoricalDtype(
                            categories=indices.get_level_values(i)
                            .map(str)
                            .map(str.rstrip)
                            .unique(),
                            ordered=True,
                        )
                    )
            for i in range(cdim):
                if hasattr(pd.DataFrame, "isetitem"):
                    sym.records.isetitem(
                        rdim + i,
                        sym.records.iloc[:, rdim + i].astype(
                            pd.CategoricalDtype(
                                categories=columns.get_level_values(i)
                                .map(str)
                                .map(str.rstrip)
                                .unique(),
                                ordered=True,
                            )
                        ),
                    )
                else:
                    sym.records.iloc[:, rdim + i] = sym.records.iloc[
                        :, rdim + i
                    ].astype(
                        pd.CategoricalDtype(
                            categories=columns.get_level_values(i)
                            .map(str)
                            .map(str.rstrip)
                            .unique(),
                            ordered=True,
                        )
                    )

            # sym.records.sort_values(sym.records.columns[:-1].tolist(), inplace=True)

    def execute(self):
        for sym in self._inst["symbols"]:
            if self._trace > 1:
                self._cdb.print_log(
                    f'Input (symbol): name: >{sym["name"]}< range: >{sym["range"]}< rowDimension: >{sym.get("rowDimension", "")}< columnDimension: >{sym.get("columnDimension", "")}< type: >{sym.get("type", "")}< valueSubstitutions: >{sym.get("valueSubstitutions", "")}< drop: >{sym.get("drop", "")}< readExcelArguments: >{sym.get("readExcelArguments", "")}<\n'
                )

            sym_name = sym["name"]
            read_excel_args = sym.get("readExcelArguments", {})
            # handle range notation sheet!range
            if "!" not in sym["range"]:
                self.connect_error(
                    f'Invalid range >{sym["range"]}<. Needs to be of format sheet_name!range'
                )
            else:
                sheet, rng = sym["range"].split("!")
                sheet = read_excel_args.get("sheet_name", sheet)
                sheet_names = [n.lower() for n in self._excel_file.sheet_names]
                try:
                    sheet = sheet_names.index(sheet.lower())
                except:
                    self.connect_error(f"Sheet >{sheet}< not found")
                nw = rng.split(":")[0]
                endrow = None
                endcol = None
                if ":" in rng:
                    se = rng.split(":")[1]
                    coord_se = openpyxl.utils.cell.coordinate_from_string(se)
                    endrow = coord_se[1] - 1
                    endcol = (
                        openpyxl.utils.cell.column_index_from_string(coord_se[0]) - 1
                    )
            coord_nw = openpyxl.utils.cell.coordinate_from_string(nw)
            startrow = coord_nw[1] - 1
            startcol = openpyxl.utils.cell.column_index_from_string(coord_nw[0]) - 1

            sym_type = sym.get("type", self._sym_type)
            cdim = sym.get("columnDimension", self._cdim)
            rdim = sym.get("rowDimension", self._rdim)
            multicolumnblankrow = sym.get(
                "multiColumnBlankRow", self._multicolumnblankrow
            )

            # enforce sufficient ranges
            if endrow is not None and endcol is not None:
                if endrow - startrow < cdim:
                    self.connect_error(
                        f"Invalid range >{rng}<. With columnDimension: >{cdim}< the range must include at least {cdim+1} rows."
                    )
                if endcol - startcol < rdim:
                    self.connect_error(
                        f"Invalid range >{rng}<. With rowDimension: >{rdim}< the range must include at least {rdim+1} columns."
                    )

            if self._trace > 1:
                self._cdb.print_log(
                    f'Processed Input (symbol): name: >{sym["name"]}< range: >{sym["range"]}< rowDimension: >{rdim}< columnDimension: >{cdim}< type: >{sym_type}< valueSubstitutions: >{sym.get("valueSubstitutions", "")}< drop: >{sym.get("drop", "")}< readExcelArguments: >{sym.get("readExcelArguments", "")}<'
                )

            self._read_excel(
                sym_name,
                sym_type,
                rdim,
                cdim,
                multicolumnblankrow,
                sheet,
                startrow,
                startcol,
                endrow,
                endcol,
                read_excel_args,
                sym.get("valueSubstitutions", {}),
                sym.get("drop", None),
            )

        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            for name, sym in self._cdb._container.data.items():
                self._cdb.print_log(
                    f"Connect Container symbol={name}:\n {sym.records}\n"
                )

    def close(self):
        self._excel_file.close()
