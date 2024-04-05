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

import pandas as pd
import numpy as np
from gams import transfer as gt
from gams.connect.agents.connectagent import ConnectAgent


class SQLReader(ConnectAgent):

    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        self._connection_args = inst.get("connectionArguments", {})
        self._cnctn_type = inst.get("connectionType", "sqlite")
        self._sym_type = inst.get("type", "par")
        self._dtype_map = inst.get("dTypeMap", {})
        self._trace = inst.get("trace", cdb.options.get("trace", 0))
        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)

    def open(self):
        if self._trace > 1:
            self._cdb.print_log(
                f'Input (root): connection: >{self._inst["connection"]}< connectionArguments: >{self._inst.get("connectionArguments", "")}< connectionType: >{self._inst.get("connectionType", "")}< trace: >{self._inst.get("trace", "")}< type: >{self._inst.get("type", "")}< dTypeMap: >{self._inst.get("dTypeMap", "")}<\n'
            )
            self._cdb.print_log(
                f"Processed Input (root): connectionArguments: >{self._connection_args}< connectionType: >{self._cnctn_type}< trace: >{self._trace}< type: >{self._sym_type}< dTypeMap: >{self._dtype_map}<\n"
            )

        if self._cnctn_type == "sqlalchemy":
            import sqlalchemy

            con_str = sqlalchemy.engine.URL.create(**self._inst["connection"])
            self._engine = sqlalchemy.create_engine(con_str, **self._connection_args)
            self._conn = self._engine.connect()

        else:
            if self._cnctn_type in ["pyodbc", "access"]:
                import pyodbc as sql
            elif self._cnctn_type == "postgres":
                import psycopg2 as sql
            elif self._cnctn_type == "mysql":
                import pymysql as sql
            elif self._cnctn_type == "sqlserver":
                import pymssql as sql
            else:  # sqlite3 by default
                import sqlite3 as sql
            self._engine = sql.connect(
                **self._inst["connection"], **self._connection_args
            )
            self._conn = self._engine.cursor()

    def execute(self):
        try:
            for sym in self._inst["symbols"]:

                sym_name = sym["name"]
                sym_type = sym.get("type", self._sym_type)
                read_sql_args = sym.get("readSQLArguments", {})
                dtype_map = sym.get("dTypeMap", self._dtype_map)
                value_col = sym.get("valueColumns", None)
                if value_col is None:
                    if sym_type == "par":
                        value_col = "lastCol"  # the last column will be a value column per default
                    elif sym_type == "set":
                        value_col = ""  # all columns will be index columns per default
                value_sub = sym.get("valueSubstitutions", {})
                index_sub = sym.get("indexSubstitutions", {})
                stack = False
                index_sub_flag = False

                if self._trace > 1:
                    self._cdb.print_log(
                        f'Input (symbol): name: >{sym["name"]}< type: >{sym.get("type", "")}< query: >{sym["query"]}<  valueColumns: >{sym.get("valueColumns", "")}< indexSubstitutions: >{sym.get("indexSubstitutions", "")}< valueSubstitutions: >{sym.get("valueSubstitutions", "")}< dTypeMap: >{sym.get("dTypeMap", "")}< readSQLArguments: >{sym.get("readSQLArguments", "")}<\n'
                    )
                    self._cdb.print_log(
                        f"Processed Input (symbol): type: >{sym_type}< valueColumns: >{value_col}< indexSubstitutions: >{index_sub}< valueSubstitutions: >{value_sub}< dTypeMap: >{dtype_map}< readSQLArguments: >{read_sql_args}<\n"
                    )
                if self._cnctn_type == "sqlalchemy":
                    df = pd.read_sql(sql=sym["query"], con=self._conn, **read_sql_args)
                else:
                    if (
                        len(read_sql_args) > 0
                    ):  # cannot pass an empty dictionary for pyODBC
                        self._conn.execute(sym["query"], read_sql_args)
                    else:
                        self._conn.execute(sym["query"])
                    df = pd.DataFrame.from_records(
                        self._conn.fetchall(),
                        columns=[col[0] for col in self._conn.description],
                    )

                if self._trace > 2:
                    self._cdb.print_log(f"DataFrame({sym_name}) after reading:\n{df}\n")

                cols = list(df.columns)

                if len(dtype_map) > 0:
                    df = df.astype(
                        {c: dtype_map[c] for c in cols if c in dtype_map.keys()}
                    )

                if type(value_col) == str:
                    if value_col == "lastCol":
                        dim = len(cols) - 1
                        if dim > 0:
                            df.set_index(cols[:-1], inplace=True)
                        elif sym_type == "set":
                            self.connect_error(
                                "Dimension must be greater than 0 for a set."
                            )
                    elif value_col == "":
                        if sym_type == "set":
                            df.set_index(cols, inplace=True)
                            index_sub_flag = True
                            dim = len(cols)
                        elif sym_type == "par":
                            self.connect_error(
                                f"A parameter requires at least one value column."
                            )
                    else:
                        self.connect_error(
                            f"Invalid string >{value_col}< for valueColumns was passed."
                        )
                elif type(value_col) == list:
                    if len(value_col) == 0:
                        if sym_type == "set":
                            df.set_index(cols, inplace=True)
                            index_sub_flag = True
                            dim = len(cols)
                        else:
                            self.connect_error(
                                f"A Parameter requires at least one value column."
                            )
                    else:
                        if all(x in cols for x in value_col):
                            index_col = [c for c in cols if c not in value_col]
                            if index_col != []:
                                df.set_index(index_col, inplace=True)
                            dim = len(index_col)
                            if (
                                len(value_col) > 1
                            ):  # automatically stack column names to index for more than one value/text column
                                stack = True
                                dim += 1
                        else:
                            not_in_df = list(set(value_col) - set(cols))
                            self.connect_error(
                                f"The following column(s) do not exist in the DataFrame({sym_name}): {not_in_df}"
                            )

                if self._trace > 2:
                    self._cdb.print_log(
                        f"DataFrame({sym_name}) after .set_index():\n{df}"
                    )

                domain = []
                if dim > 0:
                    if stack:
                        columns = df.columns
                        # stack from column axis to index axis
                        df = df.stack(dropna=False)
                        if dim == 1:
                            df = df.droplevel(
                                level=0
                            )  # drop pandas default index level
                        if self._trace > 1:
                            self._cdb.print_log(
                                f"Automatically stack column names to index for more than one value/text column."
                            )
                        if self._trace > 3:
                            self._cdb.print_log(
                                f"DataFrame({sym_name}) after stack:\n{df}"
                            )

                    # write relaxed domain information
                    domain = [str(d) if d is not None else "*" for d in df.index.names]

                    df = df.reset_index()  # reset indices
                    if self._trace > 3:
                        self._cdb.print_log(
                            f"DataFrame({sym_name}) after .reset_index():\n{df}"
                        )
                    if len(index_sub.keys()) > 0:  # index substitution
                        if (
                            index_sub_flag
                        ):  # case where all columns in the dataFrame are set to indices
                            df = df.replace(index_sub)
                        else:  # inplace=True is not working since df.iloc[:,:-1] makes a copy
                            df.iloc[:, :-1] = df.iloc[:, :-1].replace(index_sub)
                        if self._trace > 3:
                            self._cdb.print_log(
                                f"DataFrame({sym_name}) after index substitution:\n{df}"
                            )
                        if stack: # categories substitution
                            columns = pd.Index(pd.Series(columns).replace(index_sub))

                df = df.fillna(value=np.nan)
                if len(value_sub.keys()) > 0:  # value substitution
                    df.iloc[:, -1].replace(value_sub, inplace=True)
                    if self._trace > 3:
                        self._cdb.print_log(
                            f"DataFrame({sym_name}) after value substitution:\n{df}"
                        )

                if sym_type == "par":
                    sym = gt.Parameter(self._cdb._container, sym_name, domain=domain)
                    df = df.dropna()
                else:
                    sym = gt.Set(self._cdb._container, sym_name, domain=domain)
                    df = df.dropna()
                    if len(value_col) > 0 or value_col != "":
                        df[df.columns[-1]] = df[df.columns[-1]].astype(str)

                df.columns = range(df.columns.size)  # reset column names

                if self._trace > 2:
                    self._cdb.print_log(
                        f"Final DataFrame({sym_name}) that will be processed by GAMSTransfer:\n{df}"
                    )

                if not df.empty:
                    sym.setRecords(df)

                if stack:
                    if hasattr(pd.DataFrame, "isetitem"):
                        sym.records.isetitem(
                            dim - 1,
                            sym.records.iloc[:, dim - 1].astype(
                                pd.CategoricalDtype(
                                    categories=columns.unique(), ordered=True
                                )
                            ),
                        )
                    else:
                        sym.records.iloc[:, dim - 1] = sym.records.iloc[
                            :, dim - 1
                        ].astype(
                            pd.CategoricalDtype(
                                categories=columns.unique(), ordered=True
                            )
                        )

        finally:
            if self._cnctn_type == "sqlalchemy":
                self._engine.dispose()
            else:
                self._conn.close()

        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            for name, sym in self._cdb._container.data.items():
                self._cdb.print_log(
                    f"Connect Container symbol={name}:\n {sym.records}\n"
                )
