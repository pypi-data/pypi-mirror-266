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
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import pandas as pd
from gams import transfer as gt
import copy
from gams.connect.agents.connectagent import ConnectAgent
from typing import Any, List, Optional, Union


class CSVReader(ConnectAgent):
    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        self._file = os.path.abspath(inst["file"])
        self._name = inst["name"]
        self._index_cols = inst.get("indexColumns", None)
        self._index_sub = inst.get("indexSubstitutions", None)
        self._value_cols = inst.get("valueColumns", None)
        self._value_sub = inst.get("valueSubstitutions", None)
        self._text_cols = inst.get("textColumns", None)
        self._trace = inst.get("trace", cdb.options.get("trace", 0))
        if self._value_cols is not None and self._text_cols is not None:
            self.connect_error("Cannot specify both valueColumns and textColumns.")
        self._text_sub = inst.get("textSubstitutions", None)
        self._header = inst.get("header", True)
        self._multiheader = True if isinstance(self._header, list) else False
        self._header = self._get_header()
        if self._multiheader:
            if self._value_cols:
                self.connect_error(
                    "Cannot specify valueColumns if the data has a multi-row"
                    " header. All columns that are not indexColumns will be"
                    " read as valueColumns."
                )
            if self._text_cols:
                self.connect_error(
                    "Cannot specify textColumns if the data has a multi-row"
                    " header. Reading sets with multi-row headers is not"
                    " supported."
                )
            if isinstance(self._index_cols, list) and all(
                isinstance(col, str) for col in self._index_cols
            ):
                self.connect_error(
                    "The CSVReader with multi-row header does not support to"
                    " specify indexColumns as column names. Please provide"
                    " column positions instead."
                )

        self._names = inst.get("names", None)
        self._n_rows = inst.get("nRows", None)
        self._skip_rows = inst.get("skipRows", None)
        if isinstance(self._skip_rows, list):
            # pandas skiprows is 0-indexed
            self._skip_rows = [i - 1 for i in self._skip_rows]

        self._auto_col = inst.get("autoColumn", None)
        if self._multiheader and self._auto_col:
            self.connect_error("Cannot use autoColumn with multi-row header.")

        self._auto_row = inst.get("autoRow", None)
        if self._multiheader and self._auto_row:
            self.connect_error("Cannot use autoRow with multi-row header.")

        self._stack = inst.get("stack", False)
        if (
            self._stack
            and self._header is None
            and self._names is None
            and self._auto_col is None
        ):
            self.connect_error("Cannot stack without a header, names or autoColumn.")

        self._field_sep = inst.get("fieldSeparator", ",")
        self._decimal_sep = inst.get("decimalSeparator", ".")
        self._thousands_sep = inst.get("thousandsSeparator", None)
        self._quoting = inst.get("quoting", 0)

        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)

        self._read_csv_args = {
            "header": self._header,
            "names": self._names,
            "nrows": self._n_rows,
            "skiprows": self._skip_rows,
            "sep": self._field_sep,
            "decimal": self._decimal_sep,
            "thousands": self._thousands_sep,
            "quoting": self._quoting,
        }
        self._read_csv_args.update(self._inst.get("readCSVArguments", {}))

    def _get_header(self) -> Optional[Union[int, list]]:
        """
        Returns the header value that will be provided to pandas
        read_csv method according to the user input

        Returns
        -------
        int | list | None
            Header value
        """

        # For non-multirow header, user inputs are booleans (True or False).
        if self._header is False:
            return None

        if self._header is True:
            return 0

        if isinstance(self._header, list):
            # pandas header is 0-indexed
            return [i - 1 for i in self._header]

    def _get_last_column(self) -> str:
        """Returns the position of the last column

        Returns
        -------
        str
            Position of the last column
        """
        read_header_args = copy.deepcopy(self._read_csv_args)
        if self._header is not None or self._names is not None:
            read_header_args.update({"nrows": 0})

            if self._trace > 1:
                self._cdb.print_log(
                    "Calculate symbolic constant lastCol by reading the"
                    " header row. Arguments for reading the header"
                    f" row:\n{read_header_args}"
                )

        else:
            read_header_args.update({"header": None, "nrows": 1})

            if self._trace > 1:
                self._cdb.print_log(
                    "Calculate symbolic constant lastCol by reading the"
                    " first line of data. Arguments for reading the first"
                    f" line of data:\n{read_header_args}"
                )

        header_row = pd.read_csv(self._file, **read_header_args)

        return str(len(header_row.columns))

    def _convert_to_valid_pd_cols(self, cols: Any) -> Union[List[int], List[str]]:
        """Converts user provided indexColumns, valueColumns or textColumns
        to valid pandas columns

        Parameters
        ----------
        cols : Any
            Columns provided by the user

        Returns
        -------
        list
            Column positions or names
        """

        if isinstance(cols, str):
            if "lastcol" in cols.lower():
                last_col = self._get_last_column()
                cols = cols.lower().replace("lastcol", last_col)
            try:
                positions = [
                    (
                        list(
                            range(
                                *[
                                    int(value) + index
                                    for index, value in enumerate(position.split(":"))
                                ]
                            )
                        )
                        if ":" in position
                        else [int(position)]
                    )
                    for position in cols.split(",")
                ]

                # convert to 0-indexed
                cols = [i - 1 for sublist in positions for i in sublist]
            except Exception:
                self.connect_error(
                    "Column assignation as string can only include"
                    " integers, comma (,), colon (:) and symbolic constant"
                    " lastCol."
                )
        elif isinstance(cols, list):
            if all(isinstance(i, int) for i in cols):
                cols = [i - 1 for i in cols]  # convert to 0-indexed
        elif isinstance(cols, int):
            cols = [cols - 1]
        else:
            cols = []

        return cols

    def _get_dtypes(
        self,
        index_col: Optional[Union[List[int], List[str]]],
        usecols: Union[List[int], List[str]],
    ) -> dict:
        """Returns the data types for index and text columns

        Parameters
        ----------
        index_col : List[int] | List[str] | None
            Index columns to be used for read_csv
        usecols : List[int] | List[str]
            All columns to be used

        Returns
        -------
        dict
            Updated data types for columns
        """
        col_dtype = {}

        if index_col is not None:
            col_dtype.update({i: str for i in index_col})

        if len(self._text_cols) > 0:
            text_col = [sorted(usecols).index(i) for i in self._text_cols]
            col_dtype.update({i: str for i in text_col})

        return col_dtype

    def _substitute_index(self, df: pd.DataFrame) -> None:
        """Inplace index substitution

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to be manipulated
        """
        if self._sym_type == "set" and len(self._text_cols) == 0:
            df.replace(self._index_sub, inplace=True)
        else:
            df.iloc[:, :-1] = df.iloc[:, :-1].replace(self._index_sub)

        if self._trace > 3:
            self._cdb.print_log(f"DataFrame after index substitution:\n{df}")

    def _substitute_text(self, df: pd.DataFrame) -> None:
        """Inplace text substitution

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to be manipulated
        """
        df.iloc[:, -1].replace(self._text_sub, inplace=True)

        if self._trace > 3:
            self._cdb.print_log(f"DataFrame after text substitution:\n{df}")

    def _substitute_values(self, df: pd.DataFrame):
        """Inplace value substitution

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to be manipulated
        """
        df.iloc[:, -1].replace(self._value_sub, inplace=True)

        if self._trace > 3:
            self._cdb.print_log(f"DataFrame after value substitution:\n{df}")

    def _generate_row_labels(self, df: pd.DataFrame) -> None:
        """Generates row labels for autoRow option

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to be manipulated
        """
        if self._index_cols:
            index_frame = df.index.to_frame()
            index_frame.insert(
                0,
                "autoRow",
                [self._auto_row + str(i + 1) for i in range(len(df.index))],
                True,
            )

            df.index = pd.MultiIndex.from_frame(index_frame)
        else:
            df.rename(
                {i: self._auto_row + str(i + 1) for i in list(df.index)},
                axis="index",
                inplace=True,
            )

        if self._trace > 3:
            self._cdb.print_log(f"DataFrame after inserting autoRow:\n{df}")

    def _generate_column_labels(self, df: pd.DataFrame) -> None:
        """Generates columns labels for autoColumn option

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to be manipulated
        """
        if (self._header is not None or self._names is not None) and self._trace > 1:
            self._cdb.print_log("autoColumn overrides existing column names.")

        df.rename(
            {c: self._auto_col + str(i + 1) for i, c in enumerate(list(df.columns))},
            axis="columns",
            inplace=True,
        )

        if self._trace > 3:
            self._cdb.print_log(f"DataFrame after inserting autoColumn:\n{df}")

    def _set_categoricals(
        self, symbol: Union["gt.Set", "gt.Parameter"], dim: int, columns: list
    ) -> None:
        """Sets the categoricals for the Gams Transfer symbol records

        Parameters
        ----------
        symbol : gt.Set | gt.Parameter
            Symbol for setting the categoricals
        dim : int
            Dimension to set the categories on
        columns : list
            Column names for categories
        """
        if hasattr(pd.DataFrame, "isetitem"):
            symbol.records.isetitem(
                dim,
                symbol.records.iloc[:, dim].astype(
                    pd.CategoricalDtype(
                        categories=columns.map(str).map(str.rstrip).unique(),
                        ordered=True,
                    )
                ),
            )
        else:
            symbol.records.iloc[:, dim] = symbol.records.iloc[:, dim].astype(
                pd.CategoricalDtype(
                    categories=columns.map(str).map(str.rstrip).unique(),
                    ordered=True,
                )
            )

    def _stack_multiheader(self, df: pd.DataFrame) -> pd.DataFrame:
        """Stacks column names to index for a multi-row header

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to be stacked

        Returns
        -------
        pd.DataFrame
            Stacked DataFrame
        """
        # Make index and column names unique
        df.columns.names = [f"column_{i}" for i in range(len(df.columns.names))]

        df.index.names = [f"row_{i}" for i in range(len(df.index.names))]

        # Stack columns to index
        df = df.stack(level=df.columns.names, dropna=False)

        return df

    def execute(self):
        self._index_cols = self._convert_to_valid_pd_cols(self._index_cols)
        self._value_cols = self._convert_to_valid_pd_cols(self._value_cols)
        self._text_cols = self._convert_to_valid_pd_cols(self._text_cols)

        usecols = self._index_cols + self._value_cols + self._text_cols
        if not all(type(i) == str for i in usecols) and not all(
            type(i) == int for i in usecols
        ):
            self.connect_error(
                "Index/value/text columns must be either given as positions or"
                " names not both."
            )
        if len(self._value_cols) > 1 or len(self._text_cols) > 1:
            if self._header is None and self._names is None and self._auto_col is None:
                self.connect_error(
                    "More than one value/text column requires a header, names"
                    " or autoColumn."
                )
            else:
                # Stack columns to index for more than one value/text cols
                self._stack = True
        elif self._multiheader:
            # Stack columns to index for multi-row header
            self._stack = True

        if self._index_cols:
            if all(type(i) == int for i in usecols) and not self._multiheader:
                index_col = [sorted(usecols).index(i) for i in self._index_cols]
            else:
                index_col = self._index_cols
        else:
            index_col = None

        # default dtype of index and text columns should be string
        if "dtype" not in self._read_csv_args.keys():
            dtypes = self._get_dtypes(index_col, usecols)
            self._read_csv_args.update({"dtype": dtypes})

        self._read_csv_args.update({"index_col": index_col})

        # Multi-row header does not support usecols, therefore, we only
        # support reading all columns and not a subset
        if not self._multiheader:
            self._read_csv_args.update({"usecols": usecols})

        if self._trace > 1:
            self._cdb.print_log(
                f"Arguments for reading the CSV file:\n{self._read_csv_args}"
            )

        df = pd.read_csv(self._file, **self._read_csv_args)

        if self._trace > 2:
            self._cdb.print_log(
                f"Raw DataFrame directly after reading the CSV file:\n{df}"
            )

        dim = len(self._index_cols)
        # write relaxed domain information
        if dim == 0:
            domain = []
        else:
            domain = [str(d) if d is not None else "*" for d in df.index.names]

        if self._auto_row is not None and not df.index.empty:
            self._generate_row_labels(df)

            dim += 1
            domain.insert(0, "*")

        if self._auto_col is not None and not df.columns.empty:
            self._generate_column_labels(df)

            if self._stack:
                dim += 1
                domain.append("*")

        elif self._stack:
            if self._multiheader:
                dim += len(self._header)
                domain.extend(
                    [str(d) if d is not None else "*" for d in df.columns.names]
                )
            else:
                dim += 1
                domain.append("*")

        if dim > 0:
            self._sym_type = "par" if self._value_cols or self._multiheader else "set"

            if self._stack:
                columns = df.columns

                # stack from column axis to index axis
                if self._multiheader:
                    df = self._stack_multiheader(df)
                else:
                    df = df.stack(dropna=False)

                if dim == 1 or (self._multiheader and dim == columns.nlevels):
                    # drop pandas default index level
                    df = df.droplevel(level=0)

                if self._trace > 1:
                    self._cdb.print_log(
                        "Automatically stack column names to index for more"
                        " than one value/text column."
                    )
                if self._trace > 3:
                    self._cdb.print_log(f"DataFrame after stack:\n{df}")

            df = df.reset_index()

            if self._trace > 3:
                self._cdb.print_log(f"DataFrame after .reset_index():\n{df}")

            # index substitution
            if self._index_sub is not None:
                self._substitute_index(df)

                # Substitute in categoricals
                if self._stack:
                    if self._multiheader:
                        mod_columns = []
                        for i in range(columns.nlevels):
                            c = columns.get_level_values(level=i)
                            mod_columns.append(pd.Series(c).replace(self._index_sub))
                        columns = pd.MultiIndex.from_arrays(mod_columns)
                    else:
                        columns = pd.Index(pd.Series(columns).replace(self._index_sub))

        else:
            if self._value_cols or self._multiheader:
                self._sym_type = "par"
            else:
                self.connect_error("Set is missing index column(s).")

        if self._sym_type == "par":
            if self._value_sub:
                self._substitute_values(df)
            df.dropna(inplace=True)

            sym = gt.Parameter(self._cdb._container, self._name, domain=domain)
        else:
            if self._text_cols and self._text_sub:
                self._substitute_text(df)

            df.dropna(inplace=True)
            sym = gt.Set(self._cdb._container, self._name, domain=domain)

        # reset the index to the default integer index
        df = df.reset_index(drop=True)

        if self._trace > 2:
            self._cdb.print_log(
                "Final DataFrame that will be processed by" f" GAMSTransfer:\n{df}"
            )

        sym.setRecords(df)

        if dim > 0 and self._stack:
            if self._multiheader:
                # Reset domain labels
                sym.domain_labels = domain
                # Set categoricals to preserve uel order
                for i in range(columns.nlevels):
                    c = columns.get_level_values(level=i)
                    c_dim = dim - columns.nlevels + i
                    self._set_categoricals(sym, c_dim, c)
            else:
                # Set categoricals to preserve uel order
                self._set_categoricals(sym, dim - 1, columns)

        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")

        if self._trace > 2:
            self._cdb.print_log(
                f"Connect Container symbol={self._name}:\n {sym.records}\n"
            )
