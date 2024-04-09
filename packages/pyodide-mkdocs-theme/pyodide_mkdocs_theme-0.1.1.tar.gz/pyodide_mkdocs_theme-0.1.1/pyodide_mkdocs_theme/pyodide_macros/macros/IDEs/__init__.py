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

# pylint: disable=invalid-name, missing-module-docstring


from functools import wraps
import re
from typing import Literal, Optional, Union

from ...tools_and_constants import ScriptSection
from ...parsing import build_code_fence
from ...plugin.maestro_IDE import MaestroIDE
from .ide_files_data import IdeFilesExtractor
from .ide import Ide





def _IDE_maker(env:MaestroIDE, mode:str):
    """
    @script_name: Partial path from the directory holding the sujet.md file, to the one holding
                  all the other required files, ending with the common prefix for the exercice.
                  Ex:   "exo" to extract:   "exo.py", "exo_corr.py", "exo_test.py", ...
                      "sub_exA/exo" for:  "sub_exA/exo.py", "sub_exA/exo_corr.py", ...
    @MAX:         Number of tries before the solution becomes visible (default=5).
    @SANS:        String of spaces or coma separated python functions or modules/packages the
                  user cannot use. By default, nothing is forbidden.
                      - Every string section that matches a builtin callable forbid that function
                        by replacing it with another function which will raise an error if called
                      - Every string section prefixed with a fot forbids a method call. Here a
                        simple string containment check is done opn the user's code, to check it
                        does not contain the desired method name with the dot before it.
                      - Any other string section is considered as a module name and doing an
                        import (in any way/syntax) involving that name will raise an error.
    @SIZE:        Max number of lines of the IDE (default=30).
    @ID:          Optional. To use to differentiate two IDEs using the same python root file.
    @WHITE:       String of spaces or coma separated python modules/packages that have to be
                  preloaded before the code restrictions (@SANS) are applied.
    @LOGS:        If True, failing assertions without feedback during the private tests will
                  be augmented automatically with the code of the assertion itself. If None,
                  use the global `show_code_on_failed_assertions` plugin value, defined in
                  `mkdocs.yml`, to determine what to do (default=None).
    @REC_LIMIT:   Setup a specific recursion limit value for the runtime (-1 if not used)
    @TERM_H:      Number of lines to use for the terminal size (ignored for vertical terminals)
    """

    @wraps(_IDE_maker)
    def wrapped(
        script_name: str = "",
        MAX: Union[int, Literal["+"]] = 5,
        SANS: str = "",
        SIZE: int = 30,
        ID: int = None,
        WHITE: str = "",
        LOGS: Optional[bool] = None,
        REC_LIMIT: int = -1,
        TERM_H: int = 10,
    ) -> str:
        return Ide(
            env, script_name, mode, MAX, SANS, SIZE, WHITE, ID, LOGS, REC_LIMIT, TERM_H
        ).make_ide()

    wrapped.__name__ = wrapped.__qualname__ = 'IDE' + mode.strip('_')
    return wrapped




def IDE(env:MaestroIDE):
    """ To build editor+terminal on 2 rows """
    return _IDE_maker(env, "")


def IDEv(env:MaestroIDE):
    """ To build editor+terminal on 2 columns """
    return _IDE_maker(env, "_v")







def section(env:MaestroIDE):
    """
    Insert the given section from the python file.
    Note: To use only on python scripts holding all the sections for the IDE macros. For regular
          files, use the `py` macro or regular code fences with file inclusions (for performances
          reasons).
    """
    @wraps(section)
    def _section(script_name:str, section_name:ScriptSection, ID:Optional[int]=None):
        file_data = IdeFilesExtractor(env, script_name)
        content = file_data.get_section(section_name)

        id_pattern = "" if ID is None else rf",\s*ID\s*=\s*{ ID }\b\s*"
        macro_pattern = rf"""['"]{ script_name }['"]\s*,\s*['"]{ section_name }['"]{ id_pattern }"""
        ide_jinja_reg = re.compile( rf"section\(\s*{ macro_pattern }" )
        indent = env.get_indent_in_current_page(ide_jinja_reg)
        out = build_code_fence(content, indent, lang='python')
        return out

    return _section
