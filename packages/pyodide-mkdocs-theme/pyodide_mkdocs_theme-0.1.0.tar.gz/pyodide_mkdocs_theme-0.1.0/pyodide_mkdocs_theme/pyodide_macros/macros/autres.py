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
Additional macros, never used in CodEx...
"""
# pylint: disable=unused-argument

import os
from typing import Union
from functools import wraps
from ..paths_utils import get_sibling_of_current_page, to_uri
from ..plugin.maestro_base_and_indent import BaseMaestro
from ..plugin.maestro_extras import MaestroExtras




def numworks(env:BaseMaestro):
    """ wut...? """

    @wraps(numworks)
    def wrapped():
        return (
            f"""<iframe src="{env.scripts_url}numworks/simulator.html" width="100%" height="500"></iframe>"""
        )
    return wrapped





def python_carnet(env:BaseMaestro):
    """Renvoie du HTML pour embarquer un fichier `carnet.ipynb` dans un notebook
    + Basthon est la solution 2021, RGPD ok
    """

    @wraps(python_carnet)
    def wrapped(
        carnet: str = "",
        aux: str = "",
        module: str = "",
        auxs=None,
        modules=None,
        hauteur: int = 700,
        chemin_relatif: bool = True,
    ) -> str:

        if chemin_relatif:
            chemin = env.variables.site_root + os.path.dirname(env.page.url.rstrip("/")) + "/"
        else:
            chemin = env.scripts_url

        lien = "https://notebook.basthon.fr/?"
        if carnet != "":
            lien += f"from={chemin}{carnet.lstrip('./')}&"
        else:
            lien += f"from={env.scripts_url}py_vide.ipynb&"

        if aux != "":
            lien += f"aux={chemin}{aux.lstrip('./')}&"
        if auxs is not None:
            for aux in auxs:
                lien += f"aux={chemin}{aux.lstrip('./')}&"

        if module != "":
            lien += f"module={chemin}{module.lstrip('./')}&"
        if modules is not None:
            for module in modules:
                lien += f"module={chemin}{module.lstrip('./')}&"

        return (
            f"<iframe src={lien} width=100% height={hauteur} onload=\"window.scrollTo({{ top: 0, behavior: 'smooth' }});\"></iframe>"
            + f"[Lien dans une autre page]({lien}){{target=_blank}}"
        )
    return wrapped





def python_ide(env:BaseMaestro):
    """Renvoie du HTML pour embarquer un fichier `script` dans une console
    + Basthon est la solution 2021, RGPD ok
    """

    @wraps(python_ide)
    def wrapped(
        script: str = "",
        aux: str = "",
        module: str = "",
        auxs=None,
        modules=None,
        hauteur: int = 700,
        chemin_relatif: bool = True,
    ) -> str:

        if chemin_relatif:
            chemin = env.variables.site_root + os.path.dirname(env.page.url.rstrip("/")) + "/"
        else:
            chemin = env.scripts_url

        lien = "https://console.basthon.fr/?"
        if script != "":
            lien += f"from={chemin}{script.lstrip('./')}&"
        else:
            lien += "script=eJwDAAAAAAE"

        if aux != "":
            lien += f"aux={chemin}{aux.lstrip('./')}&"
        if auxs is not None:
            for aux in auxs:
                lien += f"aux={chemin}{aux.lstrip('./')}&"

        if module != "":
            lien += f"module={chemin}{module.lstrip('./')}&"
        if modules is not None:
            for module in modules:
                lien += f"module={chemin}{module.lstrip('./')}&"

        return (
            f"<iframe src={lien} width=100% height={hauteur} onload=\"window.scrollTo({{ top: 0, behavior: 'smooth' }});\"></iframe>"
            + f"[Lien dans une autre page]({lien}){{target=_blank}}"
        )
    return wrapped





def html_fig(env:BaseMaestro):
    """Renvoie le code HTML de la figure n° `num`"""

    @wraps(html_fig)
    def wrapped(num: int) -> str:

        # NON TESTÉ !
        fig_html = get_sibling_of_current_page(env, env.docs_dir_path, f'figures/fig_{ num }.html', rel_to_docs=True)

        return f'--8<-- "{ to_uri(fig_html) }"'
    return wrapped





def exercice(env:MaestroExtras):
    """ wut...? """

    @wraps(exercice)
    def wrapped(var: bool = True, prem: Union[int, None] = None) -> str:
        # si var == False, alors l'exercice est placé dans une superfence.
        if prem is not None:
            env.compteur_exo = prem
        root = f"Exercice { env.compteur_exo }"
        return f"""exo \"{root}\"""" if var else '"' + root + '"'
    return wrapped





def cours(env:BaseMaestro):
    """ wut...? """

    @wraps(cours)
    def wrapped() -> str:
        return 'success "Cours"'
    return wrapped





def ext(env:BaseMaestro):
    """ wut...? """

    @wraps(ext)
    def wrapped() -> str:
        return 'ext "Pour aller plus loin"'
    return wrapped





def tit(env:BaseMaestro):
    """ Generate a Tasklist In Table """

    @wraps(tit)
    def wrapped(ch: str = "", text: str = "") -> str:
        # Tasklist In Table
        checked = 'checked=""' if ch == "x" else ""
        return f"""<ul class="task-list"><li class="task-list-item">\
            <label class="task-list-control"><input type="checkbox" {checked}>\
            <span class="task-list-indicator"></span>\
            </label>{text}</li></ul>"""
    return wrapped



def mult_col(env:BaseMaestro):
    """ wut...? """

    @wraps(mult_col)
    def wrapped(*text):
        joined = ''.join(f"""<td><b style="font-size:1.2em">{ column }</td>""" for column in text)
        cmd = f"""<table style="border-color:transparent;background-color:transparent"><tr>{ joined }</tr></table>"""
        return cmd
    return wrapped
