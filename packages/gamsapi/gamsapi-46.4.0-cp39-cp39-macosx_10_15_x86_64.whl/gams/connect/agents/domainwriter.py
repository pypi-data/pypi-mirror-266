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

from gams import transfer as gt
import pandas as pd
import re
from gams.connect.agents.connectagent import ConnectAgent


class DomainWriter(ConnectAgent):

    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        self._symbols = inst.get("symbols", [])
        self._write_all = inst.get("writeAll", "auto")
        if self._write_all == "auto":
            self._write_all = True if self._symbols == [] else False

        self._dropDomainViolations = inst.get("dropDomainViolations", False)
        self._trace = inst.get("trace", cdb.options.get("trace", 0))
        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)

    def execute(self):
        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            for name, sym in self._cdb._container.data.items():
                self._cdb.print_log(
                    f"Connect Container symbol={name}:\n {sym.records}\n"
                )
        if self._write_all:
            if self._dropDomainViolations:
                self._cdb._container.dropDomainViolations()
        else:
            for sym in self._symbols:
                regex = r'(?P<name>[a-zA-Z0-9_]+)(\((?P<domains>[a-zA-Z0-9_,"\']+)\))?'
                ms = re.fullmatch(regex, sym["name"])
                sname = ms.group("name")
                if ms.group("domains"):
                    sdom = ms.group("domains").split(",")
                else:
                    sdom = []
                if sname not in self._cdb._container:
                    self.connect_error(
                        f"Symbol '{sname}' not found in Connect database."
                    )
                ssym = self._cdb._container[sname]
                ddv = sym.get("dropDomainViolations", self._dropDomainViolations)
                if ddv in ["before", True]:
                    ssym.dropDomainViolations()
                if len(sdom) > 0 and len(sdom) == len(ssym.domain):
                    new_domain = []
                    for d in sdom:
                        if d.startswith(('"', "'")):
                            new_domain.append(d[1:-1])
                        else:
                            if d not in self._cdb._container:
                                self.connect_error(
                                    f"Domain set '{d}' not found in Connect database."
                                )
                            dsym = self._cdb._container[d]
                            assert (
                                type(dsym) in [gt.Set, gt.Alias] and dsym.dimension == 1
                            )
                            new_domain.append(dsym)
                    if self._trace > 0:
                        self._cdb.print_log(f"New domain for {sname}: {new_domain}\n")
                    ssym.domain = new_domain
                    if ddv in ["after", True]:
                        ssym.dropDomainViolations()
        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            for name, sym in self._cdb._container.data.items():
                self._cdb.print_log(
                    f"Connect Container symbol={name}:\n {sym.records}\n"
                )
