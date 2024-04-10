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
# pylint: disable=multiple-statements, attribute-defined-outside-init, unused-argument


import re
from collections import defaultdict
from typing import ClassVar, Dict, List, Optional, Set, Tuple, Union
from pathlib import Path

from mkdocs.exceptions import BuildError
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation
from mkdocs.plugins import event_priority


from ..tools_and_constants import INSERTIONS_KINDS, PageUrl
from ..pages_and_ides_configs import (
    IdeConfigKey,
    PageConfiguration,
    ScriptKind
)
from ..pyodide_logger import logger
from ..parsing import eat, encrypt_string
from ..scripts_templates import SCRIPTS_TEMPLATES

from .maestro_tools import AutoCounter
from .maestro_base_and_indent import BaseMaestro










class MaestroIDE(BaseMaestro):
    """ Holds the global logic related to the IDE macros """


    encryptCorrectionsAndRems: ClassVar[bool] = True
    """
    Use xor encryption or not for the correction and remarques. This value is tied to the
    equivalent in the global JS context (updated through build tools).
    """

    ENCRYPTION_TOKEN: ClassVar[str] = "ENCRYPTION_TOKEN"
    """
    Denote the start and end point of the content of the div tag holding correction and/or remark.
    (only used in the python layer: it is either removed in the on_page_context hook, or it's just
    not inserted at all if the encryptCorrectionsAndRems is False)
    """

    MIN_RECURSION_LIMIT: ClassVar[int] = 20
    """
    Minimum recursion depth allowed.
    """

    HDR_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"#\s*-+\s*(?:HDR|ENV)\s*-+\s*#", flags=re.IGNORECASE
    )
    """
    Old fashion way of defining the `env` code in the python source file (still supported).
    """


    terminal_count: int = AutoCounter()
    """
    Number of empty terminals (per site count. Related to the terminal() macro).
    """

    ide_count: int = AutoCounter()
    """
    Number of empty IDEs (per site count. Used for IDE without python files).
    """

    _editors_ids:  Set[str]
    """
    Store the ids of all the created IDEs, to enforce their uniqueness.
    """

    _scripts_or_link_tags_to_insert: Dict[ScriptKind,str]
    """
    UI formatting scripts to insert only in pages containing IDEs or terminals.
    Note that the values are all the scripts and/or css tags needed for the key kind,
    all joined together already, as a template string expecting the variable `to_base`.

    Defined once, through a call to register_js_and_css_tags at star building time.
    """

    _pages_configs: Dict[PageUrl, PageConfiguration]
    """
    Represent the configurations of every IDE in every Page of the documentation.
    """



    def on_config(self, config:MkDocsConfig):

        self.terminal_count = 0
        self.ide_count = 0
        self._editors_ids = set()
        self._pages_configs = defaultdict(lambda: PageConfiguration(self))
        self._scripts_or_link_tags_to_insert = {}

        self.register_js_and_css_tags(SCRIPTS_TEMPLATES)

        super().on_config(config)   # pylint: disable=no-member



    @event_priority(2000)
    def on_page_context(self,_ctx, page:Page, *, config:MkDocsConfig, nav:Navigation):
        """
        Spot pages in which corrections and remarks have been inserted, and encrypt them.

        This hook uses high priority because the html content must be modified before the search
        plugin starts indexing stuff in it.
        """
        # pylint: disable=pointless-string-statement

        if self.is_page_with_something_to_insert(page):

            logger.debug(f"Add scripts + encrypt solutions and remarks in { page.file.src_uri }")
            """
            self._omg_they_killed_keanu("exercices/tests_feedback/", page)
            chunks = [page.content]
            """
            chunks = []
            self.chunk_and_encrypt_solutions_and_rems(page.content, chunks)
            #"""
            self.add_css_or_js_scripts(page, chunks)
            page.content = ''.join(chunks)

        if hasattr(super(), 'on_page_context'):
            super().on_page_context(_ctx, page, config=config, nav=nav)



    # ---------------------------------------------------------------------------------



    def register_if_unique(self, id_ide:str):
        """
        Check if the given id has already been used.
        If so, return False. If not, register it and return True.
        """
        if id_ide in self._editors_ids:
            return False
        self._editors_ids.add(id_ide)
        return True



    def get_hdr_and_public_contents_from(
        self, opt_path_or_content: Union[ Optional[Path], str ],
    ) -> Tuple[str,str,str]:
        """
        Extract the header code and the public content from the given file (assuming it's a
        python file or possibly None, if @path is coming from get_sibling_of_current_page).

        @returns: (header, user_content, public_tests) where header and content may be an
                  empty string.
        """
        if isinstance(opt_path_or_content,str):
            content = opt_path_or_content
        else:
            if opt_path_or_content is None or not opt_path_or_content.is_file():
                return '','',''
            content = opt_path_or_content.read_text(encoding="utf-8")

        lst = self.HDR_PATTERN.split(content)
        # If HDR tokens are present, split will return an empty string as first element, hence:
        #   - len == 1 : [content]
        #   - len == 3 : ['', hdr, content]

        if len(lst) not in (1,3):
            raise BuildError(
                f"Wrong number of HDR/ENV tokens (found { len(lst)-1 }) in:\n"
                f"{opt_path_or_content!s}"
            )

        hdr = "" if len(lst)==1 else lst[1]
        content = lst[-1].strip()
        tests_cuts = re.split(r"(?i)#\s*tests", content)
        if len(tests_cuts)>2:
            raise BuildError(
                "Found more than one time the '# ?Tests' token (case insensitive) in:\n"
                + opt_path_or_content
            )
        user_code,public_tests,*_ = map(str.strip, tests_cuts + [''])
        return hdr, user_code, public_tests






    #-----------------------------------------------------------------------
    #     Manage scripts and css to include only in some specific pages
    #-----------------------------------------------------------------------




    def register_js_and_css_tags(self, scripts_dct:Dict[ScriptKind,str]):
        """
        Done once only.
        Store and adapt the html code needed to load scripts or styles directly from the page
        content. Those will be inserted at the end of a document, but still inside the its body.
        """
        kinds_diff = set(scripts_dct) - INSERTIONS_KINDS
        assert not kinds_diff, "Unknown kind(s) of scripts: " + ', '.join(kinds_diff)

        self._scripts_or_link_tags_to_insert = {
            kind: script.replace('{{ config.plugins.pyodide_macros.rebase(base_url) }}', "{to_base}")
            for kind,script in scripts_dct.items()
        }

        logger.info("Registered js and css to insert in specific pages")
        logger.info("".join(
            f'\n{kind: >10}: ' + s.strip().replace('\n', '\n'.ljust(13))
            for kind,s in self._scripts_or_link_tags_to_insert.items()
        ))


    #---------------------------------------------------------------------------------------


    def set_current_page_js_data(self, editor_name:str, prop:IdeConfigKey, data:Union[str,int]):
        """ Store data for an IDE in the current Page """
        self._pages_configs[self.page.url].set(editor_name, prop, data)


    def set_current_page_insertion_needs(self, *kind:ScriptKind):
        """ Mark a page url as needing some specific kinds of scripts (depending on the macro
            triggering the call). """
        self._pages_configs[self.page.url].update_kinds(kind)



    def is_page_with_something_to_insert(self, page:Optional[Page]=None):
        """
        Check if the current page is marked as holding at least one thing needing a script,
        insertion or ide content.
        If @page is given, use this instance instead of the one from self.page (useful for hooks)
        """
        url = page.url if page else self.page.url
        return url in self._pages_configs


    def add_css_or_js_scripts(self, page:Page, chunks:List[str]):
        """
        Build the string needed to insert the page specific formatting scripts in the
        page that will land at the given url, updating the path to reach the location
        of the scripts in the custom_dir.

        NOTE: assumption is made that, if this method is called, it's been already
              checked that there there actually _are_ scripts to insert for this page
              (see __init__:on_post_page_macros)
        """
        page = page or self.page
        url = page.url
        going_up = self.level_up_from_current_page(url)
        page_config = self._pages_configs[url]
        page_config.dump_as_scripts(going_up, self._scripts_or_link_tags_to_insert, chunks)






    #--------------------------------------------------------------------
    #                    Solution & remarks encryption
    #--------------------------------------------------------------------



    def chunk_and_encrypt_solutions_and_rems(self, html:str, chunks:List[str]):
        """
        Assuming it's known that the @page holds corrections and/or remarks:
            - Search for the encryption tokens
            - Encrypt the content in between two consecutive tokens in the page html content.
            - Once done for the whole page, replace the page content with the updated version.
        Encryption tokens are removed on the way.
        """
        if not self.encryptCorrectionsAndRems:
            chunks.append(html)
            return

        entering = 0
        while entering < len(html):
            i,j = eat(html, self.ENCRYPTION_TOKEN, start=entering, skip_error=True)
            i,j = self._cleanup_p_tags_around_encryption_tokens(html, i, j)

            chunks.append( html[entering:i] )

            if i==len(html):
                break

            ii,entering = eat(html, self.ENCRYPTION_TOKEN, start=j)     # raise if not found
            ii,entering = self._cleanup_p_tags_around_encryption_tokens(html, ii, entering)

            solution_and_rem = html[j:ii].strip()
            encrypted = encrypt_string(solution_and_rem)
            chunks.append(encrypted)



    def _cleanup_p_tags_around_encryption_tokens(self, html:str, i:int, j:int):
        """
        mkdocs automatically surrounds the encryption token with <p> tag, so they must be removed.
        Note: Including the tags in the ENCRYPTION_TOKEN doesn't change the problem: you'd just
              get another <p> tag surrounding the token... sometimes... x/
        """
        while html[i-3:i]=='<p>' and html[j:j+4]=='</p>':
            i-=3 ; j+=4
        return i,j
