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

import copy
from gams.connect.agents.connectagent import ConnectAgent


class Options(ConnectAgent):

    @staticmethod
    def definition():
        d = copy.deepcopy(Options.cerberus())
        for k, v in d.items():
            if v["type"] == "integer":
                v["type"] = int
            elif v["type"] == "string":
                v["type"] = str
            elif v["type"] == "boolean":
                v["type"] = bool
        return d

    def __init__(self, opt_dict=None):
        super().__init__(None, None, None)
        self._options = {}
        for k, v in Options.cerberus().items():
            self._options[k] = v["default"]
        if opt_dict:
            self._options.update(opt_dict)

    def get(self, key, value=None):
        if key in self._options:
            return self._options[key]
        else:
            return value

    def __getitem__(self, key):
        return self._options[key]

    def __del__(self):
        pass

    def execute(self, inst):
        self._options.update(inst)
