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

import os
from gams import transfer as gt
import pandas as pd
import copy
from gams.connect.agents.connectagent import ConnectAgent


class GDXWriter(ConnectAgent):

    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        self._symbols = inst.get("symbols", [])
        self._write_all = inst.get("writeAll", "auto")
        if self._write_all == "auto":
            self._write_all = True if self._symbols == [] else False
        self._duplicateRecords = inst.get("duplicateRecords", "all")
        self._gdx_file = os.path.abspath(inst["file"])
        self._trace = inst.get("trace", cdb.options.get("trace", 0))
        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)

    def execute(self):
        drmap = {"none": False, "first": "first", "last": "last"}
        write_container = self._cdb._container
        if self._write_all:
            if self._trace > 0:
                self.describe_container(write_container, "Connect Container")
            if self._trace > 2:
                for name, sym in write_container.data.items():
                    self._cdb.print_log(
                        f"Connect Container symbol={name}:\n {sym.records}\n"
                    )
            if self._duplicateRecords != "all":
                write_container = copy.deepcopy(
                    self._cdb._container
                )  # make a deepopy of container since dropping duplicate records would drop records from the root container as well
                write_container.dropDuplicateRecords(keep=drmap[self._duplicateRecords])
            if not write_container.hasDuplicateRecords():
                write_container.write(self._gdx_file, eps_to_zero=False)
            else:
                dup_name_list = [
                    name
                    for name, sym in write_container.data.items()
                    if sym.hasDuplicateRecords()
                ]
                self.connect_error(
                    f"Following symbols have duplicate records: {dup_name_list}"
                )
        else:
            sym_names = []
            # Since we can't copy invalid symbols (=symbols with duplicates) we need to resolve the duplicates in the Connect container
            all_dr = any(
                sym.get("duplicateRecords", self._duplicateRecords) != "all"
                for sym in self._symbols
            )
            if all_dr:
                write_container = copy.deepcopy(self._cdb._container)

            for sym in self._symbols:
                sname = sym["name"]
                if sname not in self._cdb._container:
                    self.connect_error(
                        f"Symbol '{sname}' not found in Connect database."
                    )
                dr = sym.get("duplicateRecords", self._duplicateRecords)
                if dr != "all":
                    write_container[sname].dropDuplicateRecords(keep=drmap[dr])
                if not write_container[sname].hasDuplicateRecords():
                    sym_names.append(sname)
                else:
                    self.connect_error(f"Symbol '{sname}' has duplicate records.")
            gdx = gt.Container(system_directory=self._system_directory)
            gdx.read(write_container, sym_names)

            # Apply original categories of * domains in new Container
            for sym_name in gdx.listSymbols():
                ssym = write_container[sym_name]
                tsym = gdx[sym_name]
                if ssym.records is None:
                    continue
                for d, tdl, sdl in zip(
                    tsym.domain, tsym.domain_labels, ssym.domain_labels
                ):
                    if type(d) == str:
                        tsym.records[tdl] = tsym.records[tdl].astype(
                            pd.CategoricalDtype(
                                categories=ssym.records[sdl].cat.categories,
                                ordered=True,
                            )
                        )

            # Renaming
            if self._trace > 0:
                self._cdb.print_log(f"GDX symbols: {gdx.listSymbols()}\n")
            for sym in self._symbols:
                if "newName" in sym:
                    gdx.renameSymbol(sym["name"], sym["newName"])

            if self._trace > 0:
                self.describe_container(gdx, "GDX Container")
            if self._trace > 2:
                for name, sym in gdx.data.items():
                    self._cdb.print_log(
                        f"GDX Container symbol={name}:\n {sym.records}\n"
                    )
                    self._cdb.print_log(f"  Valid: {sym.isValid(verbose=True)}\n")
            gdx.write(self._gdx_file, eps_to_zero=False)
