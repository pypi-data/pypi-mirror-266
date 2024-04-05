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

import openpyxl
import os
import pandas as pd
from gams import transfer as gt
from gams.connect.agents.connectagent import ConnectAgent


class PandasExcelWriter(ConnectAgent):

    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        self._cdb.print_log(
            "Warning: PandasExcelWriter is deprecated and will be removed in a future release. Use ExcelWriter instead."
        )
        self._excel_file = os.path.abspath(self._inst["file"])
        if os.path.splitext(self._excel_file)[1] == ".xls":
            self.connect_error(f"The PandasExcelWriter does not support .xls files.")
        self._rdim = inst.get("rowDimension", None)
        self._trace = inst.get("trace", cdb.options.get("trace", 0))
        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)
        if (
            os.path.splitext(self._excel_file)[1] not in [".xlsx", ".xlsm"]
            and self._trace > 0
        ):
            self._cdb.print_log(
                f"Warning: Other file extensions than .xlsx and .xlsm may require installing additional Python packages. Please refer to the documentation of the PandasExcelWriter agent for more information."
            )

    def open(self):
        if self._trace > 1:
            self._cdb.print_log(
                f'Input (global): file: >{self._inst["file"]}< rowDimension: >{self._inst.get("rowDimension", "")}< trace: >{self._trace}< excelWriterArguments: >{self._inst.get("excelWriterArguments", "")}<'
            )

        excel_writer_args = self._inst.get("excelWriterArguments", {})
        if "mode" not in excel_writer_args.keys() and os.path.exists(self._excel_file):
            excel_writer_args.update({"mode": "a"})
            excel_writer_args["if_sheet_exists"] = excel_writer_args.get(
                "if_sheet_exists", "overlay"
            )
            excel_writer_args["engine"] = excel_writer_args.get("engine", "openpyxl")

        if self._trace > 2:
            self._cdb.print_log(f"excel_writer_args: >{excel_writer_args}<")
        self._writer = pd.ExcelWriter(self._excel_file, **excel_writer_args)

    def _write_excel(self, df, dim, rdim, value, value_sub, to_excel_args):
        if value_sub:
            df.iloc[:, -1].replace(value_sub, inplace=True)
        if self._trace > 2:
            self._cdb.print_log(f"After value substitution:\n{df}")

        if (
            value == "element_text" and rdim * (dim - rdim) > 0
        ):  # replace empty element_text by Y when exporting a true table
            df.loc[df[value] == "", value] = "Y"

        if dim == 0:
            df.index = ["value"]
            if self._trace > 2:
                self._cdb.print_log(f"Before to_excel (dim==0):\n{df}")
                self._cdb.print_log(f"to_excel_args: >{to_excel_args}<")
            df.to_excel(self._writer, **to_excel_args)
        elif rdim == 0:
            cols = df.columns.values.tolist()
            df["_first"] = value
            df = df.pivot(index=["_first"], columns=cols[:-1], values=[value])
            df.columns = df.columns.droplevel(0)  # remove column index "values"
            df.rename_axis([None], axis=0, inplace=True)  # remove index names
            df.rename_axis(
                [None] * dim, axis=1, inplace=True
            )  # remove column index names
            if self._trace > 2:
                self._cdb.print_log(f"Before to_excel (rdim==0):\n{df}")
                self._cdb.print_log(f"to_excel_args: >{to_excel_args}<")
            df.to_excel(self._writer, **to_excel_args)
        elif (dim - rdim) == 0:
            cols = df.columns.values.tolist()
            df["_first"] = value
            df = df.pivot(
                index=cols[:rdim], columns=["_first"], values=[value]
            ).sort_index()
            df.columns = df.columns.droplevel(0)  # remove column index "values"
            df.rename_axis([None] * rdim, axis=0, inplace=True)  # remove index names
            df.rename_axis([None], axis=1, inplace=True)  # remove column index names
            if self._trace > 2:
                self._cdb.print_log(f"Before to_excel (dim-rdim==0):\n{df}")
                self._cdb.print_log(f"to_excel_args: >{to_excel_args}<")
            df.to_excel(self._writer, **to_excel_args)
        else:
            cols = df.columns.values.tolist()
            df = df.sort_values(by=cols[rdim:dim]).reset_index(drop=True)
            df = df.pivot(
                index=cols[:rdim], columns=cols[rdim:-1], values=[value]
            ).sort_index()
            df.columns = df.columns.droplevel(0)  # remove column index "values"
            df.rename_axis([None] * rdim, axis=0, inplace=True)  # remove index names
            df.rename_axis(
                [None] * (dim - rdim), axis=1, inplace=True
            )  # remove column index names
            if self._trace > 2:
                self._cdb.print_log(f"Before to_excel (else):\n{df}")
                self._cdb.print_log(f"to_excel_args: >{to_excel_args}<")
            df.to_excel(self._writer, **to_excel_args)

    def execute(self):
        try:
            for sym in self._inst["symbols"]:
                sym_name = sym.get("name")

                if sym_name not in self._cdb._container:
                    self.connect_error(
                        f"Symbol '{sym_name}' not found in Connect database."
                    )

                gt_sym = self._cdb._container[sym_name]

                if self._trace > 0:
                    self.describe_container(self._cdb._container, "Connect Container")
                if self._trace > 2:
                    self._cdb.print_log(
                        f"Connect Container symbol >{sym_name}<:\n {gt_sym.records}\n"
                    )

                if not isinstance(gt_sym, gt.Set) and not isinstance(
                    gt_sym, gt.Parameter
                ):
                    self.connect_error(
                        f"Symbol type >{type(gt_sym)}< of symbol >{sym_name}< is not supported. Supported symbol types are set and parameter."
                    )

                if gt_sym.records is None:
                    self._cdb.print_log(f"No data for symbol >{sym_name}<. Skipping.")
                    continue

                dim = gt_sym.dimension
                df = gt_sym.records.copy(deep=True)

                if isinstance(gt_sym, gt.Set):
                    value = "element_text"
                elif isinstance(gt_sym, gt.Parameter):
                    value = "value"

                rng = sym.get("range", None)
                if not rng:
                    sheet_name = sym_name
                    rng = "A1"
                else:
                    if "!" in rng:  # handle range notation sheet!range
                        sheet_name, rng = rng.split("!")
                        if ":" in rng:
                            rng = rng.split(":")[0]
                    else:
                        self.connect_error(
                            f"Invalid range >{rng}<. Needs to be of format sheet_name!range"
                        )
                coord_nw = openpyxl.utils.cell.coordinate_from_string(rng)
                startrow = coord_nw[1] - 1
                startcol = openpyxl.utils.cell.column_index_from_string(coord_nw[0]) - 1

                to_excel_args = {
                    "sheet_name": sheet_name,
                    "startrow": startrow,
                    "startcol": startcol,
                }
                to_excel_args.update(sym.get("toExcelArguments", {}))

                rdim = sym.get("rowDimension", self._rdim)
                if rdim is None:
                    rdim = dim - 1
                if self._trace > 2:
                    self._cdb.print_log(f"rdim: >{rdim}<")

                if rdim > dim:
                    self.connect_error(
                        f"rowDimension >{rdim}< exceeds dimension of symbol >{sym_name}<"
                    )

                self._write_excel(
                    df,
                    dim,
                    rdim,
                    value,
                    value_sub=sym.get("valueSubstitutions", {}),
                    to_excel_args=to_excel_args,
                )
        finally:
            self._writer.close()
