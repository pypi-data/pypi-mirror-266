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

# pylint: disable=too-few-public-methods, missing-module-docstring

from argparse import Namespace




class AutoDescriptor:
    """ StrEnum-like property for py3.11-
        If the item string doesn't match the name anymore, one can set the wanted name
        through the constructor, without changing the property name (but F2 will most
        likely also do the trick... Unless string content is actually used somewhere...)
    """

    def __init__(self, prop:str=None):      # allow to override the property name,
        self._prop = prop

    def __set_name__(self, _, prop:str):
        self._prop = self._prop or prop

    def __get__(self, _, __):
        return self._prop






# --------------------------------------------------------------------
# Various types aliasing, to disambiguate some arguments or constants
# --------------------------------------------------------------------



PageUrl = str
""" Page url, as obtained through page.url """

EditorName = str
""" String reference in the form `editor_xxx` """



class Prefix:
    """ Enum like, holding the prefixes used to build html classes or ids in the project """

    editor_  = AutoDescriptor()
    """ To build the editor name id """

    global_ = AutoDescriptor()
    """ Extra prefix to build the id of the div holding the complete IDE thing """

    comment_ = AutoDescriptor()
    """ Extra prefix for the "toggle assertions button" """

    term_ = AutoDescriptor()
    """ Extra prefix for ids of IDE terminals """

    solution_ = AutoDescriptor()
    """ Extra prefix for the div holding the correction + REM """

    input_ = AutoDescriptor()
    """ Extra prefix for the hidden input (type=file) managing the code upload part """

    compteur_ = AutoDescriptor()
    """ Extra id prefix for the span holding the counter of an IDE """

    term_only_ = AutoDescriptor()
    """ Prefix for the id of a div holding an isolated terminal """

    solo_term_ = AutoDescriptor()
    """ [OUTDATED] Prefix for the id of the fak div associated to an isolated terminal """

    py_mk_pin_scroll_input = AutoDescriptor()     # Used in the JS part only
    """ Id input, used to mark the current the view port top value when pyodide got ready """

    py_mk_qcm_id_ = AutoDescriptor()
    """ This is actually a CLASS prefix (because it's not possible to register an html id
        on admonitions)
    """







class HtmlClass:
    """ Enum like, holding html classes used here and there in the project. """

    py_mk_hidden = AutoDescriptor()    # Was "py_mk_hide"
    """ Things that will have display:none """

    py_mk_ide = AutoDescriptor()       # But "py_mk_ide"... Lost 3 hours because of that 'h'...
    """ Identify div tags holding IDEs """

    terminal = AutoDescriptor()
    """ Identify jQuery terminals. Note: also used by them => do not change it """

    py_mk_terminal_solo = AutoDescriptor()
    """ Identify the divs that will hold isolated jQuery terminals, once they are initialized """

    py_mk_terminal_ide = AutoDescriptor()
    """ Identify divs that hold jQuery terminals under an editor, once they are initialized """

    rem_fake_h3 = AutoDescriptor()
    """ To make the "Remarques:" span in the solution admonitions look like a h3 """

    term_editor = AutoDescriptor()
    """ Prefix for the class mode of a terminal (horizontal or vertical) """

    py_mk_terminal = AutoDescriptor()
    """ Generic class for pyodide terminals (put on the div holding the jQuery terminal) """

    py_mk_wrapper = AutoDescriptor()
    """ Prefix for the class mode of the div holding an IDE """

    ide_separator = AutoDescriptor()
    """ might be used with the _v suffix """




    py_mk_admonition_qcm = AutoDescriptor()
    """ Admonition containing a QCM """

    qcm_shuffle = AutoDescriptor()
    """ The questions and items must be shuffled if present """

    qcm_hidden = AutoDescriptor()
    """ The answers will be revealed if present """

    qcm_multi = AutoDescriptor()
    """ The user can select several answers """

    qcm_single = AutoDescriptor()
    """ The user can select only one answer """









class SiblingFile(Namespace):
    """ Suffixes to use to get the names of the different files related to one problem """
    exo = '.py'
    test = '_test.py'
    corr = '_corr.py'
    rem = '_REM.md'




class ScriptSection:
    """ Name of each possible section used in a "monolithic" python file """
    hdr = AutoDescriptor("env")
    user = AutoDescriptor("code")
    corr = AutoDescriptor()
    tests = AutoDescriptor()
    secrets = AutoDescriptor()







class ScriptKind:
    """
    Identify/link the macros with their needs in terms of JS scripts to add to the page
    (not in the headers/footers)
    """
    pyodide = AutoDescriptor()
    qcm = AutoDescriptor()

    # content = AutoDescriptor()        # not used anymore => forbid it
    libs = AutoDescriptor()
    scripts = AutoDescriptor()
    extrahead = AutoDescriptor()


    @staticmethod
    def is_page_related(kind:str):
        """
        Identify if the given identifier is a ScriptKind to insert for a specific macro.
        """
        return kind in PAGES_KINDS

    @staticmethod
    def is_main_related(kind:str):
        """
        Identify if the given identifier is a Script to in sert in a block of main.html.
        """
        return kind in BLOCKS_KINDS

    @staticmethod
    def is_to_insert(kind:str):
        """
        Identify if the given identifier is a Script to in sert in a block of main.html.
        """
        return kind in INSERTIONS_KINDS



BLOCKS_KINDS = set('content libs scripts extrahead'.split())
INSERTIONS_KINDS = {s for s in dir(ScriptKind) if not s.startswith('_')
                                               and not callable(getattr(ScriptKind, s)) }
PAGES_KINDS = INSERTIONS_KINDS - BLOCKS_KINDS
