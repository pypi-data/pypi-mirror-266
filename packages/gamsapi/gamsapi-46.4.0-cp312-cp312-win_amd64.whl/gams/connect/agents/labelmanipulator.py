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

import re
from gams import transfer as gt
from gams.connect.agents.connectagent import ConnectAgent
import pandas as pd


class LabelManipulator(ConnectAgent):
    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        self._map = inst.get("map", {})
        self._case = inst.get("case", {})
        self._regex = inst.get("regex", {})
        self._code = inst.get("code", {})
        self._symbols = inst.get("symbols", [])
        self._write_all = inst.get("writeAll", "auto")
        if self._write_all == "auto":
            self._write_all = True if self._symbols == [] else False
        self._trace = inst.get("trace", cdb.options.get("trace", 0))
        self._output_set = self._code.get(
            "outputSet",
            self._regex.get("outputSet", self._case.get("outputSet", None)),
        )  # outputSet only supported by code, regex, and case mode
        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)

    def _create_output_set(self, name, map_dict):
        if name in self._cdb._container:
            self.connect_error(
                f"<{name}> specified in outputSet already exists in the Connect database."
            )
        if self._trace > 1:
            self._cdb.print_log(f"Creating output set {name}")

        map_dict = {value: key for key, value in map_dict.items() if key != value}
        output_set_data = pd.DataFrame()
        output_set_data["uni"] = map_dict.keys()
        output_set_data["element_text"] = map_dict.values()
        self._cdb._container.addSet(name, records=output_set_data)

    def execute(self):
        if self._write_all:
            sym_names = self._cdb._container.listSymbols()
        else:
            sym_names = []
            for sym in self._symbols:
                if sym["name"] not in self._cdb._container:
                    self.connect_error(
                        f"<{sym['name']}> does not exist in the Connect database."
                    )

                if "newName" in sym:
                    # Creating a new symbol in the Connect database if newName is provided
                    gt_symbol = self._cdb._container[sym["name"]]
                    if isinstance(gt_symbol, gt.Set):
                        gt.Set(
                            self._cdb._container,
                            sym["newName"],
                            gt_symbol.domain,
                            records=gt_symbol.records,
                        )
                    elif isinstance(gt_symbol, gt.Parameter):
                        gt.Parameter(
                            self._cdb._container,
                            sym["newName"],
                            gt_symbol.domain,
                            records=gt_symbol.records,
                        )
                    elif isinstance(gt_symbol, gt.Variable):
                        gt.Variable(
                            self._cdb._container,
                            sym["newName"],
                            gt_symbol.domain,
                            records=gt_symbol.records,
                        )
                    elif isinstance(gt_symbol, gt.Equation):
                        gt.Equation(
                            self._cdb._container,
                            sym["newName"],
                            gt_symbol.domain,
                            records=gt_symbol.records,
                        )
                    else:
                        self.connect_error("Data type not supported.")

                    sym_names.append(sym["newName"])
                else:
                    sym_names.append(sym["name"])

        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            for name, sym in self._cdb._container.data.items():
                self._cdb.print_log(
                    f"Connect Container symbol={name}:\n {sym.records}\n"
                )
        mapping_dictionary = {}

        # mapping functionality using a GAMS set
        if self._map:
            set_name = self._map["setName"]
            invert = self._map.get("invert", False)

            if set_name not in self._cdb._container:
                self.connect_error(
                    f"The mapping set <{set_name}> does not exist in the Connect database."
                )

            if not isinstance(self._cdb._container[set_name], gt.Set):
                self.connect_error(f"The mapping set <{set_name}> is not a set.")

            if self._cdb._container[set_name].records is None:
                self.connect_error(
                    f"The mapping set <{set_name}> is empty. Please fill it with the mapping."
                )
            if self._cdb._container[set_name].records.empty:
                self.connect_error(
                    f"The mapping set <{set_name}> is empty. Please fill it with the mapping."
                )
            if self._cdb._container[set_name].dimension != 1:
                self.connect_error(
                    f"The mapping set <{set_name}> should be 1-dimensional."
                )

            mapping_df = self._cdb._container[set_name].records
            if invert:
                mapping_df = mapping_df[mapping_df.columns[::-1]]
                mapping_df.columns = ["uni", "element_text"]

            mapping_dictionary = mapping_df.set_index("uni").to_dict()["element_text"]
            if self._write_all:
                sym_names.remove(set_name)
            if self._trace > 0:
                self._cdb.print_log(
                    f'Applying map mode for symbols <{", ".join(sym_names)}>.\n'
                )
            if self._trace > 3:
                for from_uel, to_uel in mapping_dictionary.items():
                    self._cdb.print_log(f"{from_uel}  -->  {to_uel}\n")

        # casing functionality: to change the casing of labels
        elif self._case:
            rule = self._case["rule"]
            uels = self._cdb._container.getUELs(sym_names, ignore_unused=True)
            mapping_dictionary = {label: getattr(label, rule)() for label in uels}
            if self._trace > 0:
                self._cdb.print_log(
                    f'Applying case mode for symbols <{", ".join(sym_names)}>.\n'
                )
            if self._trace > 3:
                for from_uel, to_uel in mapping_dictionary.items():
                    self._cdb.print_log(f"{from_uel}  -->  {to_uel}\n")

        # regex functionality: manipulate labels through a regex expression
        elif self._regex:
            pattern = self._regex["pattern"]
            replace = self._regex["replace"]
            uels = self._cdb._container.getUELs(sym_names, ignore_unused=True)
            mapping_dictionary = {
                label: re.sub(pattern, replace, label) for label in uels
            }
            if self._trace > 0:
                self._cdb.print_log(
                    f'Applying regex mode for symbols <{", ".join(sym_names)}>.\n'
                )
            if self._trace > 3:
                for from_uel, to_uel in mapping_dictionary.items():
                    self._cdb.print_log(f"{from_uel}  -->  {to_uel}\n")

        # code functionality: manipulate labels through a Python expression
        elif self._code:
            rule = self._code["rule"]
            rule_id = self._code.get("ruleIdentifier", "x")
            uels = self._cdb._container.getUELs(sym_names, ignore_unused=True)
            mapping_dictionary = {label: eval(rule, {rule_id: label}) for label in uels}
            if self._trace > 0:
                self._cdb.print_log(
                    f'Applying code mode for symbols <{", ".join(sym_names)}>.\n'
                )
            if self._trace > 3:
                for from_uel, to_uel in mapping_dictionary.items():
                    self._cdb.print_log(f"{from_uel}  -->  {to_uel}\n")

        self._cdb._container.renameUELs(mapping_dictionary, sym_names, allow_merge=True)
        if self._output_set:
            self._create_output_set(self._output_set, mapping_dictionary)

        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            for name, sym in self._cdb._container.data.items():
                self._cdb.print_log(
                    f"Connect Container symbol={name}:\n {sym.records}\n"
                )
