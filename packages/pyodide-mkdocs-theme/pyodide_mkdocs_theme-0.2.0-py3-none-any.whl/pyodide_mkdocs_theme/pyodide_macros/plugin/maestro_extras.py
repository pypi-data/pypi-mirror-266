"""
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
Define a class the can be passed to all macro functions, holding all the necessary data
"""
# pylint: disable=multiple-statements


from mkdocs.config.defaults import MkDocsConfig

from ..tools_and_constants import Prefix
from .maestro_base_and_indent import BaseMaestro
from .maestro_tools import AutoCounter








class MaestroExtras(BaseMaestro):
    """ Class holding the "one of"/remaining/unused functionalities """


    compteur_exo: int = AutoCounter(warn=True)
    """ Number of exercices (per page count. Related to exercice() macro)
        Can be reinitialized manually through arguments of the exercice macro.
    """

    compteur_qcms: int = AutoCounter()
    """ Number of qcm or qcs in the docs """

    def get_qcm_id(self):
        return f"{ Prefix.py_mk_qcm_id_ }{ self.compteur_qcms :0>5}"



    def on_config(self, config:MkDocsConfig):
        # pylint: disable=attribute-defined-outside-init
        self.compteur_exo = 0
        self.compteur_qcms = 0

        super().on_config(config)
