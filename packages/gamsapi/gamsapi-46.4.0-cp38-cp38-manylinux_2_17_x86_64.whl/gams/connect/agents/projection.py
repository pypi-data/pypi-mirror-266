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
import numpy as np
import pandas as pd
import copy
import re
from gams.connect.agents.connectagent import ConnectAgent


class Projection(ConnectAgent):

    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)
        self._text = inst.get("text", None)
        self._asset = inst.get("asSet", False)
        self._asparameter = inst.get("asParameter", False)
        self._trace = inst.get("trace", cdb.options.get("trace", 0))
        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)

    def split_domains(self, mo, symbol):
        if mo.group("domains"):
            dom = mo.group("domains").split(",")
            for d in dom:
                if dom.count(d) > 1:
                    self.connect_error(
                        f"Multiple use of index >{d}< in domain list of symbol >{symbol}<"
                    )
            return dom
        else:
            return []

    def ren_text(self, ssym, sdom, suffix, df):
        if (
            (type(ssym) == gt.Set and not self._text in [None, ""])
            or (
                type(ssym) in [gt.Variable, gt.Equation]
                and suffix != None
                and not self._text in [None, ""]
            )
            or (type(ssym) == gt.Parameter and not self._text in [None, ""])
        ):
            df.columns = [*df.columns[:-1], "element_text"]
            df["element_text"] = df["element_text"].astype(str)
            sdom.append("element_text")
            execcmd = 'df["element_text"] = ("' + self._text + '")'
            for i, r in enumerate(sdom):
                execcmd = execcmd.replace(
                    "{" + r + "}",
                    '" + df[df.columns[' + str(i) + ']].astype(str) + "',
                )
            exec(execcmd)
            if self._trace > 2:
                self._cdb.print_log(f"DataFrame after text adjustment:\n{df}")

    def execute(self):
        if self._trace > 1:
            self._cdb.print_log(
                f'Input: name: >{self._inst["name"]}< newName: >{self._inst["newName"]}< aggregationMethod: >{self._inst.get("aggregationMethod", "")}< trace: >{self._inst.get("trace", "")}<'
            )

        if (
            type(self._inst["name"]) == list
        ):  # list of scalars into a 1-dim parameter/var/equ
            symname_list = []
            sym_list = []
            for sname in self._inst["name"]:
                if sname not in self._cdb._container:
                    self.connect_error(
                        f"Symbol '{sname}' not found in Connect database."
                    )
                symname_list.append(sname)
                sym_list.append(self._cdb._container[sname].records)
            df = pd.concat(sym_list, ignore_index=True)
            df.insert(0, "uni_0", symname_list)
            ssym0 = self._cdb._container[symname_list[0]]
            if type(ssym0) == gt.Parameter:
                gt.Parameter(
                    self._cdb._container,
                    self._inst["newName"],
                    ["*"],
                    records=df,
                )
            elif type(ssym0) == gt.Equation:
                gt.Equation(
                    self._cdb._container,
                    self._inst["newName"],
                    ssym0.type,
                    ["*"],
                    records=df,
                )
            elif type(ssym0) == gt.Variable:
                gt.Variable(
                    self._cdb._container,
                    self._inst["newName"],
                    ssym0.type,
                    ["*"],
                    records=df,
                )
            if self._trace > 0:
                self.describe_container(self._cdb._container, "Connect Container")
            if self._trace > 2:
                self._cdb.print_log(
                    f'Connect Container symbol={self._inst["newName"]}:\n {self._cdb._container[self._inst["newName"]].records}\n'
                )
            return

        regex = r"(?P<name>[a-zA-Z0-9_]+)(\.?(?P<suffix>[a-zA-Z]*))?(\((?P<domains>[a-zA-Z0-9_,]+)\))?"
        ms = re.fullmatch(regex, self._inst["name"])
        if not ms:
            self.connect_error(f'Invalid <name>: >{self._inst["name"]}<')
        mt = re.fullmatch(regex, self._inst["newName"])
        if not mt:
            self.connect_error(f'Invalid <newName>: >{self._inst["newName"]}<')

        sdom = self.split_domains(ms, "source")
        tdom = self.split_domains(mt, "target")
        if set(tdom) - set(sdom):
            self.connect_error(
                f'Unknown index >{(set(tdom) - set(sdom))}< in <newName>: >{self._inst["newName"]}<'
            )
        if mt.group("suffix"):
            self.connect_error(
                f'No suffix allowed on <newName>: >{self._inst["newName"]}<'
            )
        map = [sdom.index(d) for d in tdom]
        sname = ms.group("name")

        if sname not in self._cdb._container:
            self.connect_error(f"Symbol '{sname}' not found in Connect database.")

        tname = mt.group("name")
        suffix = ms.group("suffix")
        if suffix == "":
            suffix = None

        ssym = self._cdb._container[sname]
        tsym_dom = [ssym.domain[d] for d in map]
        suffix_index = False
        if (
            not suffix
            and type(ssym) in [gt.Equation, gt.Variable]
            and self._asparameter
        ):
            tsym_dom.append("attribute")
            suffix_index = True

        agg_method = self._inst.get("aggregationMethod", "first")

        if self._trace > 1:
            self._cdb.print_log(
                f"Processed Input: s: >{sname}< sdom: {sdom} suffix: >{suffix}< t: >{tname}< tdom: {tdom} map: {map} aggregationMethod: >{agg_method}<"
            )
            self._cdb.print_log(f"Permutation: {map}")

        if suffix != None and type(ssym) not in [gt.Variable, gt.Equation]:
            self.connect_error(
                f"<suffix> given but symbol >{sname}< not a variable or equation"
            )
        if suffix not in [None, "l", "m", "lo", "up", "scale"]:
            self.connect_error(
                f"Unknown <suffix>: >{suffix}< (use .l, .m, .lo, .up, .scale)"
            )

        if suffix:
            if self._trace > 1:
                self._cdb.print_log(f"Creating >{tname}< as {len(tdom)}-dim parameter")
            if self._asset:
                tsym = gt.Set(self._cdb._container, tname, tsym_dom)
            else:
                tsym = gt.Parameter(self._cdb._container, tname, tsym_dom)
        else:
            if self._asset or type(ssym) == gt.Set:
                tsym = gt.Set(self._cdb._container, tname, tsym_dom)
            else:
                if self._asparameter or type(ssym) == gt.Parameter:
                    tsym = gt.Parameter(self._cdb._container, tname, tsym_dom)
                elif type(ssym) == gt.Equation:
                    tsym = gt.Equation(self._cdb._container, tname, ssym.type, tsym_dom)
                elif type(ssym) == gt.Variable:
                    tsym = gt.Variable(self._cdb._container, tname, ssym.type, tsym_dom)
                else:
                    self.connect_error(
                        f"Projection can't handle symbol type >{type(ssym)}< of symbol >{sname}<."
                    )
            if self._trace > 1:
                self._cdb.print_log(
                    f"Created >{tname}< as {len(tsym_dom)}-dim {type(tsym)}"
                )

        sdim = ssym.dimension
        tdim = tsym.dimension

        if len(sdom) != sdim:
            self.connect_error(
                f"Number of domains for <name> <> dimension of <name> ({len(sdom)}<>{sdim})"
            )

        assert (
            len(map) == tdim or len(map) + 1 == tdim and suffix_index
        ), "Number of domains for <newName> <> dimension of <newName>"
        assert (
            len(tdom) == tdim or len(tdom) + 1 == tdim and suffix_index
        ), "Number of domains for <newName> <> dimension of <newName>"
        assert (
            suffix == None or type(tsym) == gt.Parameter or self._asset
        ), "Type of <newName> needs to be parameter or asSet be True"

        suffix_dict = {
            "l": "level",
            "m": "marginal",
            "lo": "lower",
            "up": "upper",
            "scale": "scale",
        }
        if len(map) == sdim:
            if self._trace > 1:
                self._cdb.print_log(f"Permutation only!")
            assert (
                suffix != None
                or type(ssym) == type(tsym)
                or self._asset
                or suffix_index
            ), "Type of <name> <> type of <newName> and asSet==False"
            df = copy.deepcopy(self._cdb._container[sname].records)
            if not type(df) == pd.DataFrame or df.empty:
                return
            if len(map):
                colsperm = df.columns.tolist()
                for d in enumerate(map):
                    colsperm[d[0]] = df.columns.tolist()[d[1]]
                if self._trace > 2:
                    self._cdb.print_log(f"Original DataFrame:\n{df}")
                    self._cdb.print_log(f"Column permutation:\n{colsperm}")
                df = df.reindex(columns=colsperm)
                if self._trace > 2:
                    self._cdb.print_log(f"Permuted DataFrame:\n{df}")
            if suffix != None:  # drop other columns
                dropc = {
                    "l": "level",
                    "m": "marginal",
                    "lo": "lower",
                    "up": "upper",
                    "scale": "scale",
                }
                del dropc[suffix]
                df.drop(columns=dropc.values(), inplace=True)
            elif suffix_index:
                if tdim == 1:
                    df = df.stack().droplevel(0)
                    df = [kv for kv in dict(df).items()]
                else:
                    df.set_index(list(df.columns[: (tdim - 1)]), inplace=True)
                    df = df.stack().reset_index()
                if self._trace > 2:
                    self._cdb.print_log(f"Stacked DataFrame:\n{df}")
            if type(tsym) == gt.Set:
                self.ren_text(ssym, sdom, suffix, df)

        else:  # len(map) < sdim
            assert (
                suffix or len(map) == tdim or len(map) + 1 == tdim and suffix_index
            ), "Number of domains <> dimension of <newName>"
            df = copy.deepcopy(self._cdb._container[sname].records)
            if not type(df) == pd.DataFrame or df.empty:
                return
            if suffix:
                del suffix_dict[suffix]
                df.drop(columns=list(suffix_dict.values()), inplace=True)
            if self._trace > 2:
                self._cdb.print_log(f"DataFrame of {sname}:\n{df}")
            if type(tsym) == gt.Set:
                self.ren_text(ssym, sdom, suffix, df)
            dropc = self._cdb._container[sname].domain_labels[: ssym.dimension]
            df[dropc] = df[dropc].astype(str)
            if (tdim == 0 or tdim == 1 and suffix_index) and agg_method in [
                "first",
                "last",
            ]:
                df.drop(columns=dropc, inplace=True)
                if agg_method == "first":
                    df = df.iloc[0]
                else:
                    df = df.iloc[-1]
                if type(tsym) in [gt.Variable, gt.Equation]:
                    df = dict(df)
                elif suffix_index:
                    df = [kv for kv in dict(df).items()]
                if self._trace > 2:
                    self._cdb.print_log(f"Data after first/last operation:\n{df}")
            else:
                df.set_index(
                    pd.MultiIndex.from_frame(
                        df[self._cdb._container[sname].domain_labels]
                    ),
                    inplace=True,
                )
                if self._trace > 2:
                    self._cdb.print_log(f"DataFrame with index:\n{df}")
                df.drop(columns=dropc, inplace=True)
                if self._trace > 2:
                    self._cdb.print_log(f"DataFrame after dropping columns:\n{df}")
                if len(map) != 0:
                    df = df.groupby(
                        [self._cdb._container[sname].domain_labels[d] for d in map]
                    )
                func = getattr(df, agg_method)
                if not callable(func):
                    self.connect_error(
                        f"aggregationMethod <{agg_method}> is not callable."
                    )
                df = func()
                if self._trace > 2:
                    self._cdb.print_log(f"DataFrame after groupby/agg operation:\n{df}")
                if type(df) == pd.DataFrame:
                    if suffix_index:
                        df = df.stack()
                        if self._trace > 2:
                            self._cdb.print_log(f"Stacked DataFrame:\n{df}")
                    df = df.reset_index(drop=False)
                    if self._trace > 2:
                        self._cdb.print_log(
                            f"DataFrame after reset_index operation:\n{df}"
                        )

        if type(df) == pd.DataFrame and type(tsym) == gt.Set:
            if type(ssym) == gt.Set and self._text == "":
                df.drop(columns=df.columns[-1], inplace=True)
            elif (
                (type(ssym) == gt.Variable or type(ssym) == gt.Equation)
                and suffix
                and self._text in [None, ""]
            ):
                df.drop(columns=df.columns[-1], inplace=True)
            elif type(ssym) in [gt.Variable, gt.Equation] and not suffix:
                df.drop(
                    columns=["level", "marginal", "lower", "upper", "scale"],
                    inplace=True,
                )
            elif type(ssym) == gt.Parameter and self._text in [None, ""]:
                df.drop(columns=df.columns[-1], inplace=True)
        if self._trace > 2:
            self._cdb.print_log(f"DataFrame written back to {tname}:\n{df}")
        tsym.setRecords(df)

        # Apply original categories of * domains in new symbol
        if tsym.dimension > 0:
            for pos, (d, tdl) in enumerate(zip(tsym.domain, tsym.domain_labels)):
                if suffix_index and pos == tsym.dimension - 1:
                    tsym.records[tdl] = tsym.records[tdl].astype(
                        pd.CategoricalDtype(
                            categories=suffix_dict.values(), ordered=True
                        )
                    )
                elif type(d) == str:
                    tsym.records[tdl] = tsym.records[tdl].astype(
                        pd.CategoricalDtype(
                            categories=ssym.records[
                                ssym.records.columns[map[pos]]
                            ].cat.categories,
                            ordered=True,
                        )
                    )

        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            self._cdb.print_log(f"Connect Container symbol={tname}:\n {tsym.records}\n")
