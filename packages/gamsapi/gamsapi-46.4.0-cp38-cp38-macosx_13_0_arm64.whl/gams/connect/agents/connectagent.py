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

from abc import ABC, abstractmethod
import importlib.resources
import yaml
from gams.connect.errors import GamsConnectException


class ConnectAgent(ABC):
    @abstractmethod
    def __init__(self, system_directory, cdb, inst):
        """
        :param system_directory: GAMS system directory to be used.
        :param cdb: An instance of gams.connect.connectdatabase.ConnectDatabase.
        :param inst: A nested data structure consisting of dictionaries and lists containing the instructions to be executed by the connect agent.
        """
        self._system_directory = system_directory
        self._cdb = cdb
        self._inst = inst
        self._ci_sym = None
        self._trace = 0

    @classmethod
    def cerberus(cls):
        """
        Class method that returns the cerberus schema as Python data structure.
        :return: Python data structure to be used by cerberus.Validator.validate() to ensure correct format of instructions given to a connect agent.
        """
        try:
            handle = importlib.resources.files("gams.connect.agents") / "schema"
        except AttributeError:
            handle = importlib.resources.path("gams.connect.agents", "schema")

        with handle as schema_path:
            schema_file = schema_path / (cls.__name__ + ".yaml")
        schema = schema_file.read_text()
        return yaml.safe_load(schema)

    def connect_error(self, msg):
        raise GamsConnectException(msg, traceback=self._trace > 0)

    def describe_container(self, m, msg):
        self._cdb.print_log(f"{msg}\n")
        if len(m.listSets()):
            self._cdb.print_log(f"Sets:\n{      m.describeSets()      }\n")
        if len(m.listAliases()):
            self._cdb.print_log(f"Aliases:\n{   m.describeAliases()   }\n")
        if len(m.listParameters()):
            self._cdb.print_log(f"Parameters:\n{m.describeParameters()}\n")
        if len(m.listEquations()):
            self._cdb.print_log(f"Equations:\n{ m.describeEquations() }\n")
        if len(m.listVariables()):
            self._cdb.print_log(f"Variables:\n{ m.describeVariables() }\n")

    def open(self):
        """
        Called by the ConnectDatabase before execute().
        """
        pass

    @abstractmethod
    def execute(self):
        """
        Called by the ConnectDatabase after open() and before close(). This abstract method needs to be implemented by a subclass.
        """
        ...

    def close(self):
        """
        Called by the ConnectDatabase after execute().
        """
