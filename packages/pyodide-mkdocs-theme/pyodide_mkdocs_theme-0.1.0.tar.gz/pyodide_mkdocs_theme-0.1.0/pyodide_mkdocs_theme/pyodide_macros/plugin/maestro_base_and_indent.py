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
# pylint: disable=multiple-statements


import re
from typing import Dict, Optional
from pathlib import Path

from mkdocs.plugins import BasePlugin
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.exceptions import BuildError

from ...__version__ import __version__
from ..tools_and_constants import PageUrl
from ..pyodide_logger import logger
from ..parsing import eat

from .maestro_tools import ConfigExtractor
from .config import PyodideMacrosConfig







class PageIndents( Dict[PageUrl, Dict[str,str]] ):
    """ Cache storing the indentations for each jinja/macro template in all Pages.
        a page is entirely studied the first time it's seen and the result of the indentation
        levels are stored.
        The data stays correct throughout the md->html conversion because the indentation
        levels "horizontal") are not affected by the content growing ("vertical").
    """

    def _explore_page_markdown(self, env:'BaseMaestro'):
        """
        Gather the indentations for all the macros insertions (aka `{{...}}`) in the page markdown.
        Only insertions following spaces or right at the beginning of a line are extracted.

        During parsing, it is also checked that there is no  `{{` starting again inside a macro
        call (this is subject to false positives, if the call contains `"{{"`!)
        """
        dct = {}
        txt = env.page.markdown
        end = len(txt)

        i,i_cmd = eat(txt, '{{', skip_error=True)
        while i < end:

            i_next_open = eat(txt, '{{', start=i+2, skip_error=True)
            i_close, _  = eat(txt, '}}', start=i)

            # Check no nested macro calls:
            if i_next_open[0] < i_close:
                self._handle_error(
                    env,
                    f"""
Couldn't figure out the structure of macros calls in the template of the page {env.page!s} :
    {"{{"!r} at index {i}
    {"{{"!r} at index {i_next_open[0]}  << should be after the next one
    {"}}"!r} at index {i_close}
If you are trying to use {"{{"!r} or {"}}"!r}:
  - in data structures: just add some extra spaces in between.
  - inside a string: please raise an issue on { env.pmt_url }.
                    """.strip()
                )

            indent = self._extract_indentation(txt, i)
            cmd = re.sub(r'\s+', '', txt[i_cmd:i_close] )

            if env.is_macro_with_indent(cmd):
                if cmd not in dct:
                    dct[cmd] = indent
                else:
                    call_data = txt[i_cmd:i_close]
                    self._handle_error(env,
                        f"In the page { env.page.file.src_uri }: the same macro call has been "
                        "found several times (ignoring spaces).",
                        epilogue=f"\n\nCall found:\n{ call_data }"
                    )

            i,i_cmd = i_next_open      # step forward to next opening template

        self[env.page.url] = dct



    def _extract_indentation(self, txt:str, i_macro:int) -> int :
        """
        Step back in the markdown until a line feed or a non space char is found, then return
        the index of the char where the line begins or the previous "non space sequence" ends
        """
        if not i_macro:
            return ''

        i = i_macro-1
        while i>0 and txt[i].isspace() and txt[i]!='\n':
            i -= 1

        n_indent = i_macro-i-1 if txt[i]=='\n' else 0
        return ' ' * n_indent



    def get_indent(self, env:'BaseMaestro', macro_predicate:re.Pattern) -> str :
        """
        Extract the indentation needed for the given macro template call.
        @throws:    BuildError if the same macro call is found several times in the page.
        """
        page:Page = env.page
        if page.url not in self:
            self._explore_page_markdown(env)

        all_indents_in_page = self[page.url]
        indents_gen = ( indent for cmd,indent in all_indents_in_page.items()
                               if macro_predicate.match(cmd) )
        target = next( indents_gen, None)
        second = next( indents_gen, None)

        id_reason = err_msg = ""
        if target is None:
            id_reason, err_msg = "no match", (
                f"In the page { page.file.src_uri }:\nCouldn't find indentation data for the "
                f"macro call with this pattern {macro_predicate.pattern!r}."
            )
        elif second is not None:
            id_reason, err_msg = "duplicate match", (
                f"In the page { page.file.src_uri }:\nFound several macro calls matching "
                f"{macro_predicate.pattern}. This is not allowed because it could lead to "
                "very weird behaviors/bugs."
            )
        if err_msg:
            data = "\n\t>>>".join(map(repr, all_indents_in_page))
            self._handle_error(env, err_msg,
                f"\n\nRegistered indentation keys for the current page are:\n\t>>>{ data }"
                f"\n\nDebugging info:\nFirst match is: {target=!r}\nSecond match is: {second=!r}",
                id_reason=id_reason,
            )
        return target



    def _handle_error(self, env:'BaseMaestro', err_msg:str, epilogue:str='', id_reason:str=""):
        if env.show_indent_errors:
            id_reason = id_reason or "invalid call structure?"
            logger.warning(                 # pylint: disable-next=protected-access
                f"[INDENT] - Macro {env._running_macro}, in {env.page.file.src_uri} ({id_reason})"
            )
        else:
            if id_reason:
                err_msg = (
                    f"{ err_msg }\nTo disambiguate the calls, use the ID:int argument of the "
                    "macro. Do not forget to add it to every macro call of this kind in the "
                    "page!\nIf this is coming from one of your own macro, you will need to add "
                    "the related logic and argument in your code."
                )
            raise BuildError( err_msg + epilogue )








MACROS_PLUGIN_VARS_ROOT = 'variables'
PMT_MACROS_ROOT = "config"


class BaseMaestro( BasePlugin[PyodideMacrosConfig] ):
    """
    Main class, regrouping the basic configurations, properties, getters and/or constants
    for the different children classes: each of them will inherit from MaestroConfig.
    It is also used as "sink" for the super calls of other classes that are not implemented
    on the MacrosPlugin class.

    Note that, for the ConfigExtractor for to properly work, the class hierarchy has to
    extend MacrosPlugin at some point.
    """


    show_code_on_failed_assertions: bool = ConfigExtractor()
    skip_py_md_paths_names_validation: bool = ConfigExtractor()
    check_python_files: bool  = ConfigExtractor()
    soft_check: bool          = ConfigExtractor()
    load_yaml_encoding: str   = ConfigExtractor()
    _dev_mode: bool           = ConfigExtractor()
    encrypt_corrections_and_rems: bool = ConfigExtractor()
    macros_with_indents: str  = ConfigExtractor()
    show_indent_errors: bool = ConfigExtractor()
    ignore_macros_plugin_diffs: bool = ConfigExtractor()

    scripts_url: str    = ConfigExtractor("others")
    site_root: str      = ConfigExtractor("others")

    page: Page  # just as a reminder: defined by MacrosPlugin

    # global mkdocs config data:
    site_url: str = ConfigExtractor(root='_conf')
    docs_dir: str = ConfigExtractor(root='_conf')
    repo_url: str = ConfigExtractor(root='_conf')

    #----------------------------------------------------------------------------
    # WARNING: the following properties are assigned from the PyodideMacrosPlugin

    docs_dir_path: Path
    """ Current docs_dir of the project as a Path object (ABSOLUTE path) """

    docs_dir_cwd_rel: Path
    """ docs_dir Path object, but relative to the CWD, at runtime """

    _macro_with_indent_pattern:re.Pattern = None
    """
    Pattern to re.match macro calls that will need to handle indentation levels.
    Built at runtime (depends on `macro_with_indents`)
    """

    #----------------------------------------------------------------------------

    version:str = __version__

    pmt_url:str = 'https://gitlab.com/frederic-zinelli/pyodide-mkdocs-theme'


    _pages_indents: PageIndents
    """
    Cache storing the indentations for each jinja/macro template in a Page.
    A page is entirely studied the first time it's seen and the result of the indentation levels
    are stored.
    The data stays correct throughout the md->html conversion because the indentation levels
    "horizontal") are not affected by the content growing ("vertical").
    """

    _running_macro: Optional[str] = None
    """
    Name of the macro currently running (or the last one called. None if no macro called yet).
    """



    def on_config(self, config:MkDocsConfig):
        # pylint: disable=unused-argument, no-member, missing-function-docstring
        self._pages_indents = PageIndents()

        super().on_config(config)     # MacrosPlugin is actually "next in line" and has the method


    #----------------------------------------------------------------------------


    def get_indent_in_current_page(self, macro_predicate:re.Pattern):
        """
        Extract the indentation needed for the given macro template call.
        @throws:    BuildError if the same macro call is found several times in the page.
        """
        return self._pages_indents.get_indent(self, macro_predicate)


    def is_macro_with_indent(self, macro_call:str) -> bool:
        """
        Return True if the given macro call requires to register indentation data.
        This is using a white list, so that user defined macro cannot cause troubles.
        """
        return bool(self._macro_with_indent_pattern.match(macro_call))


    def level_up_from_current_page(self, url:str=None) -> str:
        """
        Return the appropriate number of ".." steps needed to build a relative url to go from the
        current page url back to the root directory.

        Note there are no trailing backslash.

        @url: relative to the docs_dir (ex: "exercices/ ..."). If None, use self.page.url instead.
        """
        url = self.page.url if url is None else url
        page_loc:Path = self.docs_dir_path / url
        segments = page_loc.relative_to(self.docs_dir_path).parts
        out = len(segments) * ['..']
        return '/'.join(out) or '.'


    #----------------------------------------------------------------------------


    def _omg_they_killed_keanu(self,page_name:str, page_on_context:Page=None):
        """ Debugging purpose only. Use as breakpoint utility.
            @page_on_context argument used when called "outside" of the macro logic (fro example,
            in external hooks)
        """
        page = page_on_context or self.page
        if page_name == page.url:
            logger.error("Breakpoint! (the CALL to this method should be removed)")


    def warn_unmaintained(self, that:str):
        """
        Generic warning message for people trying to used untested/unmaintained macros.
        """
        logger.warning(
            f"{ that.capitalize() } has not been maintained since the original pyodide-mkdocs "
            "project and may not currently work.\n"
            "Please open an issue on the pyodide-mkdocs-theme repository, providing a concrete "
            "use case so that it can be updated.\n\n"
            f"\t{ self.pmt_url }"
        )
