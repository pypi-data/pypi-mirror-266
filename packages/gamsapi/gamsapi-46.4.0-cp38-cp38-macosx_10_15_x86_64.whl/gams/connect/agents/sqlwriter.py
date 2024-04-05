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
from gams import transfer as gt
from gams.connect.agents.connectagent import ConnectAgent


class SQLWriter(ConnectAgent):

    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        # global options
        self._input_cnctn = inst["connection"]  # input db credentials/path thru user.
        self._cnctn_type = inst.get("connectionType", "sqlite")
        self._connection_args = self._inst.get("connectionArguments", {})
        self._ifExists = inst.get("ifExists", "fail")
        self._schema_name = inst.get("schemaName", None)
        self._to_sql_args = inst.get("toSQLArguments", {})
        self._trace = inst.get("trace", cdb.options.get("trace", 0))
        self._write_all = inst.get("writeAll", "auto")
        self._insertMethod = inst.get("insertMethod", "default")
        self._unstack = inst.get("unstack", False)
        self._value_sub = inst.get("valueSubstitutions", {})
        self._symbols = inst.get("symbols", [])  # symbol option

        if self._write_all == "auto":
            self._write_all = True if self._symbols == [] else False
        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)

    def open(self):
        if self._trace > 1:
            self._cdb.print_log(
                f'Input (root): connection: >{self._inst["connection"]}< connectionArguments: >{self._inst.get("connectionArguments", "")}< connectionType: >{self._inst.get("connectionType", "")}< trace: >{self._inst.get("trace", "")}< writeAll: >{self._inst.get("writeAll", "")}< ifExists: >{self._inst.get("ifExists", "")}< insertMethod: >{self._inst.get("insertMethod", "")}< schemaName: >{self._inst.get("schemaName", "")}< toSQLArguments: >{self._inst.get("toSQLArguments", "")}< unstack: >{self._inst.get("unstack", "")}< valueSubstitutions: >{self._inst.get("valueSubstitutions", "")}<\n'
            )

            self._cdb.print_log(
                f"Processed Input (root): connectionArguments: >{self._connection_args}< connectionType: >{self._cnctn_type}< trace: >{self._trace}< writeAll: >{self._write_all}< ifExists: >{self._ifExists}< insertMethod: >{self._insertMethod}< schemaName: >{self._schema_name}< toSQLArguments: >{self._to_sql_args}< unstack: >{self._unstack}< valueSubstitutions: >{self._value_sub}<\n"
            )

        if self._cnctn_type == "sqlalchemy":
            if self._insertMethod == "default":
                import sqlalchemy

                con_str = sqlalchemy.engine.URL.create(**self._input_cnctn)
                self._engine = sqlalchemy.create_engine(
                    con_str, **self._connection_args
                )
                self._conn = self._engine.connect()
            else:
                self.connect_error(
                    f"Use of insertMethod: >{self._insertMethod}< is not supported with SQLALCHEMY."
                )

        else:
            if self._cnctn_type == "pyodbc":
                import pyodbc as sql
            elif self._cnctn_type == "access":
                import pyodbc as sql
                from pathlib import Path

                if not Path(
                    self._input_cnctn["DBQ"]
                ).is_file():  # if .accdb file does not exist at the provided loc in DBQ, then create a new .accdb file
                    self._create_accdb(dbpath=self._input_cnctn["DBQ"])
                    if self._trace > 3:
                        self._cdb.print_log(
                            f'Created a new .accdb file: >{self._input_cnctn["DBQ"]}<'
                        )
            elif self._cnctn_type == "postgres":
                import psycopg2 as sql
            elif self._cnctn_type == "mysql":
                import pymysql as sql

                self._connection_args.update(
                    {"local_infile": True}
                )  # set local_infile to true for bulkInsert symbol option
            elif self._cnctn_type == "sqlserver":
                import pymssql as sql
            else:  # sqlite3 by default
                import sqlite3 as sql
            self._engine = sql.connect(**self._input_cnctn, **self._connection_args)
            self._conn = self._engine.cursor()

    def _create_new_table(self, df, tableName, schema):
        """
        Drops an exisiting table and creates a new table with the same name. Uses specific SQL queries for each DBMS flavour.
        """
        tableCols = ""
        if self._cnctn_type in [
            "access",
            "sqlserver",
            "sqlite",
        ]:  # MS-Access text columns must be of datatype `VARCHAR` & All three should enclose colNames within []
            for col, dtype in df.dtypes.items():
                if dtype == "float64":
                    tableCols += f"[{col}]" + " FLOAT,"
                elif dtype == "int64":
                    tableCols += f"[{col}]" + " BIGINT,"
                elif dtype in ["object", "category"]:
                    tableCols += f"[{col}]" + " VARCHAR(255),"

        elif self._cnctn_type == "mysql":
            for col, dtype in df.dtypes.items():
                if dtype == "float64":
                    tableCols += f"`{col}`" + " DOUBLE,"
                elif dtype == "int64":
                    tableCols += f"`{col}`" + " BIGINT,"
                elif dtype in ["object", "category"]:
                    tableCols += f"`{col}`" + " TEXT,"

        elif self._cnctn_type == "postgres":
            for col, dtype in df.dtypes.items():
                if dtype == "float64":
                    tableCols += f'"{col}"' + " FLOAT,"
                elif dtype == "int64":
                    tableCols += f'"{col}"' + " BIGINT,"
                elif dtype in ["object", "category"]:
                    tableCols += f'"{col}"' + " TEXT,"

        else:  # support for pyodbc, does not handle special character in colNames
            for col, dtype in df.dtypes.items():
                if dtype == "float64":
                    tableCols += f"({col})" + " FLOAT,"
                elif dtype == "int64":
                    tableCols += f"({col})" + " BIGINT,"
                elif dtype in ["object", "category"]:
                    tableCols += f"({col})" + " TEXT,"

        tableCols = tableCols[:-1]

        if schema:
            tableName = schema + "." + tableName

        try:
            if self._cnctn_type == "sqlserver":
                self._conn.execute(
                    f"""IF OBJECT_ID('{tableName}', 'U') IS NOT NULL DROP TABLE {tableName};"""
                )

            elif self._cnctn_type in ["mysql", "postgres", "sqlite"]:
                self._conn.execute(f"""DROP TABLE IF EXISTS {tableName};""")

            else:  # for ms-access and pyodbc
                if self._check_table(tableName, schema=None):
                    self._conn.execute(f"""DROP TABLE {tableName};""")
        except:
            self.connect_error(f"Cannot drop table >{tableName}<")

        self._conn.execute(f"""CREATE TABLE {tableName}({tableCols});""")
        self._engine.commit()
        if self._trace > 3:
            self._cdb.print_log(
                f"Created new table: >{tableName}< with columns: >{tableCols}<"
            )

    def _create_accdb(self, dbpath):
        """
        Creates an MS-Access (.accdb) file/database at provided dbpath.
        """
        import win32com.client as win32

        Access = win32.Dispatch("Access.Application")
        Access.NewCurrentDataBase(dbpath)
        Access.CloseCurrentDataBase()
        Access.Quit()  # required in order to remove access application from python memory
        del Access

    def _check_table(self, tableName, schema):
        """
        Helper function, returns True if `tableName` already exists in the DBMS.
        """
        tableExists = False
        if self._cnctn_type == "sqlite":
            self._conn.execute(
                f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}'"""
            )

        elif self._cnctn_type in ["access", "pyodbc"]:  # for ms-access
            for ele in self._conn.tables().fetchall():
                if ele[2] == tableName:
                    tableExists = True
            return tableExists

        else:  # works for postgres, mysql and sqlserver
            if schema:
                self._conn.execute(
                    f"""SELECT table_name FROM information_schema.tables
                                        WHERE table_schema = '{schema}'
                                        AND table_name = '{tableName}';"""
                )
            else:
                self._conn.execute(
                    f"""SELECT table_name FROM information_schema.tables
                                        WHERE table_name = '{tableName}';"""
                )
        if self._conn.fetchone():
            tableExists = True

        return tableExists

    def _write_native_sql(self, df, insertMethod, writeFunction_args):
        """
        The default write function when `insertMethod`= `default`.
        Uses the executemany method for inserting the rows in the DBMS.
        Applicable for SQLite, MySQL, SQL-Server, MS-Access and Pyodbc
        """
        placeHolder = "?," * (len(df.columns) - 1)
        tableName = writeFunction_args["name"]
        if df.isnull().values.any():  # replace NaN with None, for SQL NULL
            df = df.astype(object).where(pd.notnull(df), None)
        df_list = list(
            df.itertuples(index=None, name=None)
        )  # sql server does not accept nested lists, it has to be tuples
        if writeFunction_args["schema"]:
            tableName = writeFunction_args["schema"] + "." + tableName
        query = f"INSERT INTO {tableName} VALUES(" + placeHolder + "?)"
        if self._cnctn_type in ["mysql", "sqlserver"]:
            query = query.replace("?", "%s")
        self._conn.executemany(query, df_list)
        self._engine.commit()

    def _writefile_to_access(self, df, writeFunction_args):
        """
        Uses MS-Access' make-table query to create a new table from csv.
        This does not require the table to be present in the database file.
        Thus, `ifExists` behavior changes accordingly.
        """
        ifExists = writeFunction_args["if_exists"]
        tableName = writeFunction_args["name"]
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdirname:
            with tempfile.NamedTemporaryFile(
                mode="w", dir=tmpdirname, delete=False, suffix=".csv"
            ) as fp:
                df.to_csv(fp.name, index=False)
                fp.flush()
                fp.seek(0)
                fp.close()
                filename = fp.name.split("\\")[-1]
                if ifExists == "replace":
                    try:
                        self._conn.execute(f"""DROP TABLE {tableName};""")
                        self._conn.execute(
                            f"SELECT * INTO [{tableName}] FROM [text;HDR=Yes;FMT=Delimited(,);"
                            + f"Database={tmpdirname}].{filename};"
                        )
                    except:
                        self._conn.execute(
                            f"SELECT * INTO [{tableName}] FROM [text;HDR=Yes;FMT=Delimited(,);"
                            + f"Database={tmpdirname}].{filename};"
                        )
                elif (
                    ifExists == "append"
                ):  # creates a temp table `randomTemp_<tableName>` in the same db file, inserts the result of newly created temp table into the existing table
                    if self._check_table(tableName, schema=None):
                        self._conn.execute(
                            f"SELECT * INTO [randomTemp_{tableName}] FROM [text;HDR=Yes;FMT=Delimited(,);"
                            + f"Database={tmpdirname}].{filename};"
                        )
                        self._conn.execute(
                            f"INSERT INTO {tableName} SELECT * FROM [randomTemp_{tableName}];"
                        )
                        self._conn.execute(f"DROP TABLE [randomTemp_{tableName}];")
                    else:
                        self.connect_error(
                            f"Table >{tableName}< does not exists and ifExists is set to `append`."
                        )
                elif ifExists == "fail":
                    if not self._check_table(tableName, schema=None):
                        self._conn.execute(
                            f"SELECT * INTO [{tableName}] FROM [text;HDR=Yes;FMT=Delimited(,);"
                            + f"Database={tmpdirname}].{filename};"
                        )
                    else:
                        self.connect_error(
                            f"Table >{tableName}< already exist and ifExists is set to `fail`."
                        )
            self._engine.commit()

    def _write_to_postgres(self, df, insertMethod, writeFunction_args):
        """
        Helper function for handling insertion into Postgres DBs.
        default: uses .execute_batch with page_size=100 (fixed and default)
        bulkInsert: uses the .copy_expert method to stream a csv file into the DB
        """
        tableName = writeFunction_args["name"]
        if writeFunction_args["schema"]:
            tableName = writeFunction_args["schema"] + "." + tableName
        if insertMethod == "bulkInsert":
            import io

            s_buf = io.StringIO()
            df.to_csv(s_buf, index=False, header=False)
            s_buf.seek(0)
            colNames = ", ".join(f'"{ele}"' for ele in df.columns)
            query = f"""COPY {tableName} ({colNames}) FROM STDIN WITH CSV"""
            self._conn.copy_expert(query, file=s_buf)
        elif insertMethod == "default":
            from psycopg2.extras import execute_batch

            placeHolder = "%s," * (len(df.columns) - 1)
            query = f"INSERT INTO  {tableName} VALUES(" + placeHolder + "%s)"
            if df.isnull().values.any():  # replace NaN with None, for SQL NULL
                df = df.astype(object).where(pd.notnull(df), None)
            df_list = df.values.tolist()
            execute_batch(self._conn, query, df_list)
        self._engine.commit()

    def _writefile_to_sql(self, df, insertMethod, writeFunction_args):
        """
        Function to import data from file to MySQL and SQL Server DBMS
        MySQL: uses `LOAD DATA LOCAL INFILE` query to import csv, provided the infile option (OPT_LOCAL_INFILE = 1) is enabled in the DBMS
        SQL Server: `bcp`, uses the bulk-copy-program utility to import a txt file given the following exists on the system. 1)bcp utility, 2)Relevant ODBC driver. This works when operating on a remote dbms server.
                    `bulkInsert`, uses the `BULK INSERT` query to import a csv file. Does not work if operating on a Remote DBMS server.
        """
        import tempfile

        tableName = writeFunction_args["name"]
        with tempfile.TemporaryDirectory() as tmpdirname:
            with tempfile.NamedTemporaryFile(
                mode="w", dir=tmpdirname, delete=False, suffix=".csv"
            ) as fp:
                df.to_csv(fp.name, index=False, header=False)
                fp.flush()
                fp.seek(0)
                fp.close()
                if writeFunction_args["schema"]:
                    tableName = writeFunction_args["schema"] + "." + tableName

                if self._cnctn_type == "mysql":
                    import sys

                    filepath = fp.name.replace("\\", "/")
                    setVals = ", ".join(
                        ["@" + str(i + 1) for i in range(len(df.columns))]
                    )
                    linending = "\r\n" if sys.platform == "win32" else "\n"
                    query = f"""LOAD DATA LOCAL INFILE "{filepath}" INTO TABLE {tableName} 
                                FIELDS TERMINATED BY ','
                                ENCLOSED BY '"'
                                LINES TERMINATED BY '{linending}'
                                ({setVals})"""
                    set_variables = ", ".join(
                        [
                            "`{0}`=NULLIF(@{1},'')".format(col, i + 1)
                            for i, col in enumerate(df.columns)
                        ]
                    )
                    query += "SET " + set_variables + ";"
                    self._conn.execute(query)
                elif self._cnctn_type == "sqlserver":
                    if insertMethod == "bulkInsert":
                        self._conn.execute(
                            f"""BULK INSERT {tableName}
                                FROM "{fp.name}"
                                WITH (FORMAT = 'CSV', FIRSTROW = 1,KEEPIDENTITY)"""
                        )
                    elif insertMethod == "bcp":
                        from subprocess import run, PIPE
                        from shutil import which

                        cmd = f"""bcp {tableName} in "{fp.name}" -U "{self._input_cnctn['user']}" -P "{self._input_cnctn['password']}" -S "{self._input_cnctn['host']},{self._input_cnctn['port']}" -q -c -t "," -d {self._input_cnctn['database']}"""
                        if self._trace > 2:
                            self._cdb.print_log(f"Command to be executed: {cmd}\n")
                        if which(
                            "bcp"
                        ):  # check if bcp is present on the system, returns path if present else None
                            cmd_res = run(
                                cmd,
                                stdout=PIPE,
                                stderr=PIPE,
                                universal_newlines=True,
                                shell=True,
                            )  # shell=True is required for successful run on Linux
                            if cmd_res.returncode != 0:
                                self.connect_error(
                                    f"Error occured while running bcp utility.\n {cmd_res.stdout}"
                                )
                        else:
                            self.connect_error(f"bcp utility not found on the system.")
            self._engine.commit()

    def _write_sql(
        self,
        df,
        dim,
        unstack,
        value,
        value_sub,
        insertMethod,
        to_sql_args,
        writeFunction_args,
    ):
        """
        Main function to process the incoming write request. Depending on the provided `connectionType` and `insertMethod`, dispatches a pre-defined write function.
        """
        if value_sub:
            df.iloc[:, -1].replace(value_sub, inplace=True)
            if self._trace > 2:
                self._cdb.print_log(f"After value substitution:\n{df}")

        if unstack and dim > 0:
            if (
                value == "element_text"
            ):  # replace empty element_text by Y when exporting a true table
                df.loc[df[value] == "", value] = "Y"
            cols = list(df.columns)
            if dim > 1:
                df = df.pivot(index=cols[0:-2], columns=cols[-2], values=value)
                df.reset_index(inplace=True, drop=False)
            else:
                df = df.set_index(cols[0]).T.reset_index(drop=True)
            df.rename_axis([None], axis=1, inplace=True)  # remove column index names
            if self._trace > 3:
                self._cdb.print_log(f"DataFrame after unstack:\n{df}")
        elif dim > 0:
            df.sort_values(df.columns[:-1].tolist(), inplace=True)
            if self._trace > 3:
                self._cdb.print_log(f"DataFrame after sort:\n{df}")

        if self._cnctn_type == "sqlalchemy":
            if self._trace > 2:
                self._cdb.print_log(f"DataFrame before .to_sql():\n{df}")
                self._cdb.print_log(f"to_sql_args: >{to_sql_args}<")
            df.to_sql(con=self._conn, **to_sql_args)

        else:
            if self._trace > 2:
                self._cdb.print_log(f"DataFrame before writing:\n{df}")
                self._cdb.print_log(f"writeFunction_args: >{writeFunction_args}<")

            try:
                dispatcher = {
                    "sqlite": {"default": self._write_native_sql},
                    "postgres": {
                        "default": self._write_to_postgres,
                        "bulkInsert": self._write_to_postgres,
                    },
                    "mysql": {
                        "default": self._write_native_sql,
                        "bulkInsert": self._writefile_to_sql,
                    },
                    "sqlserver": {
                        "default": self._write_native_sql,
                        "bcp": self._writefile_to_sql,
                        "bulkInsert": self._writefile_to_sql,
                    },
                    "pyodbc": {"default": self._write_native_sql},
                    "access": {
                        "default": self._write_native_sql,
                        "bulkInsert": None,
                    },
                }
                writeFunction = dispatcher[self._cnctn_type][insertMethod]
            except KeyError as err:
                self.connect_error(
                    f"insertMethod >{err}< is not valid for connection type >{self._cnctn_type}<. Valid insertion methods are >{list(dispatcher[self._cnctn_type].keys())}<"
                )

            tableName = writeFunction_args["name"]
            schema = writeFunction_args["schema"]

            if (
                writeFunction == None
            ):  # done separately because access has unique `ifexists` methods
                self._writefile_to_access(df, writeFunction_args)
            else:
                if writeFunction_args["if_exists"] == "replace":
                    self._create_new_table(df=df, tableName=tableName, schema=schema)
                    writeFunction(df, insertMethod, writeFunction_args)

                elif writeFunction_args["if_exists"] == "append":
                    if self._check_table(tableName=tableName, schema=schema):
                        writeFunction(df, insertMethod, writeFunction_args)
                    else:
                        self.connect_error(
                            f"Table >{tableName}< does not exist in the database and ifExists is set to >append<."
                        )

                elif writeFunction_args["if_exists"] == "fail":
                    if not self._check_table(tableName=tableName, schema=schema):
                        self._create_new_table(
                            df=df, tableName=tableName, schema=schema
                        )
                        writeFunction(df, insertMethod, writeFunction_args)
                    else:
                        self.connect_error(
                            f"Table >{tableName}< already exists in the database and ifExists is set to >fail<."
                        )

    def execute(self):
        try:
            if self._trace > 0:
                self.describe_container(self._cdb._container, "Connect Container")

            if self._write_all:
                self._symbols = []
                for name, sym in self._cdb._container.data.items():
                    if type(sym) in [gt.Set, gt.Parameter]:
                        self._symbols.append({"name": name})

            for sym in self._symbols:
                sym_name = sym.get("name")

                if sym_name not in self._cdb._container:
                    self.connect_error(
                        f"Symbol '{sym_name}' not found in Connect database."
                    )

                table_name = sym["tableName"] if not self._write_all else sym_name
                schema = sym.get("schemaName", self._schema_name)
                exists = sym.get("ifExists", self._ifExists)
                unstack = sym.get("unstack", self._unstack)
                value_sub = sym.get("valueSubstitutions", self._value_sub)
                insertMethod = sym.get("insertMethod", self._insertMethod)
                gt_sym = self._cdb._container[sym_name]
                if self._trace > 1:
                    self._cdb.print_log(
                        f'Input (symbol): name: >{sym["name"]}< tableName: >{sym.get("tableName", "")}< ifExists: >{sym.get("ifExists", "")}< insertMethod: >{sym.get("insertMethod", "")}< schemaName: >{sym.get("schemaName", "")}< unstack: >{sym.get("unstack", "")}< valueSubstitutions: >{sym.get("valueSubstitutions", "")}< toSQLArguments: >{sym.get("toSQLArguments", "")}<\n'
                    )
                    self._cdb.print_log(
                        f"Processed Input (symbol): tableName: >{table_name}< ifExists: >{exists}< insertMethod: >{insertMethod}< schemaName: >{schema}< unstack: >{unstack}< valueSubstitutions: >{value_sub}<\n"
                    )

                if self._trace > 2:
                    self._cdb.print_log(
                        f"Connect Container symbol={sym_name}:\n {gt_sym.records}\n"
                    )

                if not isinstance(gt_sym, gt.Set) and not isinstance(
                    gt_sym, gt.Parameter
                ):
                    self.connect_error(
                        f"Symbol type >{type(gt_sym)}< of symbol >{sym_name}< is not supported. Supported symbol types are set and parameter."
                    )

                if gt_sym.records is None:
                    self._cdb.print_log(f"No data for symbol {sym_name}. Skipping.")
                    continue

                if isinstance(gt_sym, gt.Set):
                    value = "element_text"
                elif isinstance(gt_sym, gt.Parameter):
                    value = "value"

                dim = gt_sym.dimension
                df = gt_sym.records.copy(deep=True)

                to_sql_args = {
                    "name": table_name,
                    "schema": schema,
                    "if_exists": exists,
                    "index": False,
                }
                to_sql_args.update(sym.get("toSQLArguments", self._to_sql_args))

                writeFunction_args = {
                    "name": table_name,
                    "schema": schema,
                    "if_exists": exists,
                }

                self._write_sql(
                    df,
                    dim,
                    unstack,
                    value,
                    value_sub,
                    insertMethod,
                    to_sql_args,
                    writeFunction_args,
                )
        finally:
            if self._cnctn_type == "sqlalchemy":
                self._engine.dispose()
            else:
                self._conn.close()
