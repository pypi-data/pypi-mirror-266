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
Simple elements introduced through macros
(code block with language and indentation, empty terminal, ...)
"""
# pylint: disable=unused-argument


import re
from pathlib import Path
from functools import wraps

from .. import html_builder as Html
from ..plugin.maestro_IDE import MaestroIDE
from ..plugin.maestro_base_and_indent import BaseMaestro
from ..parsing import build_code_fence
from ..paths_utils import get_sibling_of_current_page
from ..tools_and_constants import HtmlClass, Prefix, ScriptKind





def script(
    env:MaestroIDE,
    macro:str,
    docs_dir:Path,
    nom:str,
    *,
    lang:str='python',
    stop=None,
    ID:int=None
) -> str:
    """
    Renvoie le script dans une balise bloc avec langage spécifié

    - macro: permet de retrouver le niveau d'indentation de l'appel de macro
    - lang: le nom du lexer pour la coloration syntaxique
    - nom: le chemin du script relativement au .md d'appel
    - stop: si ce motif est rencontré, il n'est pas affichée, ni la suite.
    """
    target = get_sibling_of_current_page(env, docs_dir, nom, tail='.py')
    _,content,public_tests = env.get_hdr_and_public_contents_from(target)

    # Split again if another token is provided
    if stop is not None:
        # rebuild "original" if another token is provided
        if public_tests:
            content = f"{ content }\n\n# Tests\n\n{ public_tests }"
        content = re.split(stop, content)[0]

    id_pattern = "" if ID is None else rf".*?,\s*ID\s*=\s*{ ID }"
    macro_pattern = f"""['"]{ nom }['"]"""
    ide_jinja_reg = re.compile( rf"{ macro }\(\s*{ macro_pattern }{ id_pattern }" )
    indent = env.get_indent_in_current_page(ide_jinja_reg)
    out = build_code_fence(content, indent, lang=lang)
    return out



def py(env:MaestroIDE):
    """
    Macro python rapide, pour insérer le contenu d'un fichier python. Les parties HDR sont
    automatiquement supprimées, de même que les tests publiques. Si un argument @stop est
    fourni, ce dot être une chaîne de caractère compatible avec re.split, SANS matching groups.
    Tout contenu après ce token sera ignoré (token compris) et "strippé".

    ATTENTION: Ne marche pas sur les exercices avec tous les codes python dans le même fichier.
    """
    @wraps(py)
    def wrapped(nom: str, stop=None, ID:int=None) -> str:
        return script(env, 'py', env.docs_dir_path, nom, stop=stop, ID=ID)
    return wrapped


def py_sujet(env:MaestroIDE):
    """
    Macro python rapide, pour un sujet sans les tests => code formaté seulement, non modifiable.

    ATTENTION: Ne marche pas sur les exercices avec tous les codes python dans le même fichier.
    """
    @wraps(py_sujet)
    def wrapped(nom: str, stop=None, ID:int=None) -> str:
        return script(env, 'py_sujet', env.docs_dir_path, nom, stop=stop, ID=ID)
    return wrapped






def terminal(env:MaestroIDE):
    """
    Create a Python Terminal.
    @SIZE(=6): number of lines (height) of the terminal
    """

    @wraps(terminal)
    def wrapped(SIZE:int=6) -> str:

        env.set_current_page_insertion_needs(ScriptKind.pyodide)

        term_id = f'{ Prefix.term_only_ }{ env.terminal_count }'
        classes = " ".join((HtmlClass.py_mk_terminal_solo, HtmlClass.py_mk_terminal))
        div     = Html.terminal(term_id, kls=classes, n_lines_h=SIZE )
        return div

    return wrapped
