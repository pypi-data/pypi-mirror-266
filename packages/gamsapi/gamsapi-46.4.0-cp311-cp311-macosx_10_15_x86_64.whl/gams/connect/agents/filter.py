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
import copy
from gams.connect.agents.connectagent import ConnectAgent
import re


class Filter(ConnectAgent):

    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        self._value_filters = inst.get("valueFilters", [])
        self._name = inst.get("name")
        self._new_name = inst.get("newName")
        self._trace = inst.get("trace", cdb.options.get("trace", 0))

        if self._name not in self._cdb._container:
            self.connect_error(f"Symbol '{self._name}' not found in Connect database.")

        self._sym = self._cdb._container[self._name]
        self._label_filters = {}
        for f in inst.get("labelFilters", []):
            c = f["column"]
            if c != "all":
                c = c - 1
            if c in self._label_filters:
                self.connect_error(f"More than one filter for column {c+1}.")
            self._label_filters[c] = f
        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)

    def _filter_labels(self, df, f, c):
        if c == "all":
            for c in range(0, self._sym.dimension):
                df = self._filter_labels(df, f, c)
        else:
            if c >= self._sym.dimension:
                self.connect_error(
                    f"Invalid column index({c+1}) for symbol with dimension {self._sym.dimension}"
                )
            if "keep" in f:
                df = df.loc[df.iloc[:, c].isin(f["keep"])]
            elif "reject" in f:
                df = df.loc[~df.iloc[:, c].isin(f["reject"])]
            elif "regex" in f:
                regex = re.compile(f["regex"])
                df = df.loc[df.iloc[:, c].str.fullmatch(regex)]
        return df

    def _filter_values(self, df, f, c, skip_trace=False):
        if type(self._sym) == gt.Set:
            self.connect_error(
                "Value filters are not supported for symbols of type set."
            )
        rule_identifier = f.get("ruleIdentifier", "x")
        rule = f.get("rule", "")
        rule = (
            "(" + rule.replace(rule_identifier, f'df["{c}"]') + ")"
            if rule
            else "[True]*len(df)"
        )

        include_sv = ""
        exclude_sv = ""
        if f.get("eps", True):
            include_sv += f' | (gt.SpecialValues.isEps(df["{c}"]))'
        else:
            exclude_sv += f' & (~gt.SpecialValues.isEps(df["{c}"]))'
        if f.get("infinity", True):
            include_sv += f' | (gt.SpecialValues.isPosInf(df["{c}"]))'
        else:
            exclude_sv += f' & (~gt.SpecialValues.isPosInf(df["{c}"]))'
        if f.get("negativeInfinity", True):
            include_sv += f' | (gt.SpecialValues.isNegInf(df["{c}"]))'
        else:
            exclude_sv += f' & (~gt.SpecialValues.isNegInf(df["{c}"]))'
        if f.get("undf", True):
            include_sv += f' | (gt.SpecialValues.isUndef(df["{c}"]))'
        else:
            exclude_sv += f' & (~gt.SpecialValues.isUndef(df["{c}"]))'
        if f.get("na", True):
            include_sv += f' | (gt.SpecialValues.isNA(df["{c}"]))'
        else:
            exclude_sv += f' & (~gt.SpecialValues.isNA(df["{c}"]))'
        rule += exclude_sv + include_sv

        if self._trace > 1 and not skip_trace:
            self._cdb.print_log(f'Applying rule for column "{c}": {rule}')
        if c == "all":
            if type(self._sym) == gt.Parameter:
                value_columns = ["value"]
            elif type(self._sym) in [gt.Variable, gt.Equation]:
                value_columns = [
                    "level",
                    "marginal",
                    "lower",
                    "upper",
                    "scale",
                ]
            for c in value_columns:
                df = self._filter_values(df, f, c, True)
        else:
            df = eval(f"df.loc[({rule})]", {"df": df, "gt": gt})
        return df

    def execute(self):
        if self._trace > 1:
            self._cdb.print_log(
                f'Input: name: >{self._inst["name"]}< newName: >{self._inst["newName"]}< trace: >{self._inst.get("trace", "")}<'
            )

        if type(self._sym) == gt.Set:
            tsym = gt.Set(self._cdb._container, self._new_name, self._sym.domain)
        elif type(self._sym) == gt.Parameter:
            tsym = gt.Parameter(self._cdb._container, self._new_name, self._sym.domain)
        elif type(self._sym) == gt.Variable:
            tsym = gt.Variable(
                self._cdb._container,
                self._new_name,
                self._sym.type,
                self._sym.domain,
            )
        elif type(self._sym) == gt.Equation:
            tsym = gt.Equation(
                self._cdb._container,
                self._new_name,
                self._sym.type,
                self._sym.domain,
            )
        else:
            self.connect_error("Data type not supported.")

        df = copy.deepcopy(self._sym.records)
        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            self._cdb.print_log(f"Original DataFrame:\n{df}")
        for c in self._label_filters:
            f = self._label_filters[c]
            if self._trace > 1:
                self._cdb.print_log(
                    f'Input (labelFilters): column: >{f["column"]}< keep: >{f.get("keep", "")}< reject: >{f.get("reject", "")}< regex: >{f.get("regex", "")}<'
                )
            if c == "all":
                df = self._filter_labels(df, f, c)
                if self._trace > 2:
                    self._cdb.print_log(
                        f"DataFrame after label filter for column 'all':\n{df}"
                    )
            else:
                df = self._filter_labels(df, f, c)
                if self._trace > 2:
                    self._cdb.print_log(
                        f"DataFrame after label filter for column {c+1}:\n{df}"
                    )

        val_cols = [f["column"] for f in self._value_filters]
        if len(val_cols) != len(set(val_cols)):
            for c in set(val_cols):
                val_cols.remove(c)
            self.connect_error(
                f"More than one value filter for column(s) {set(val_cols)}."
            )

        for f in self._value_filters:
            c = f["column"]
            if self._trace > 1:
                self._cdb.print_log(
                    f'Input (valueFilters): column: >{f["column"]}< ruleIdentifier: >{f.get("ruleIdentifier", "x")}< rule: >{f.get("rule", "")}< eps: >{f.get("eps", "True")}< infinity: >{f.get("infinity", "True")}< negativeInfinity: >{f.get("negativeInfinity", "True")}< undf: >{f.get("undf", "True")}< na: >{f.get("na", "True")}<'
                )
            df = self._filter_values(df, f, c)
            if self._trace > 2:
                self._cdb.print_log(
                    f'DataFrame after value filter for column "{c}":\n{df}'
                )
        tsym.setRecords(df)

        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            self._cdb.print_log(
                f"Connect Container symbol={self._new_name}:\n {tsym.records}\n"
            )
