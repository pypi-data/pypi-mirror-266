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



import re
from pathlib import Path
from dataclasses import dataclass
import subprocess
from typing import ClassVar, Dict, Optional, Union

from mkdocs.exceptions import BuildError

from ...plugin.maestro_IDE import MaestroIDE
from ...paths_utils import (
    get_sibling_of_current_page,
    read_file,
)
from ...pyodide_logger import logger
from ...tools_and_constants import ScriptSection, SiblingFile




CWD = Path.cwd()




@dataclass
class IdeFilesExtractor:
    """
    ENTRY POINT: takes a script_name (IDE macro first argument) and extract from that all
    the necessary data from the different files.
    With `script_name` being denoted X and F being the stem of the current md file, the
    extracted files may be:
        1. X.py and X_REM.md, where the py file contains all the needed python code, separated
            by the pyodide python tokens: `# --- PYODIDE:{kind} --- #` or so
        2. X.py, X_text.py, X_corr.py and X_REM.md
        3. scripts/F/X.py, scripts/F/X_text.py, scripts/F/X_corr.py and scripts/F/X_REM.md

    The order gives the precedence. Way "1" is excluding the 2 others (except for the REM file)
    """

    env: MaestroIDE
    script_name: str
    id: Optional[int] = None

    #-----------------------------

    exo_py: Optional[Path] = None
    """ Path to the master python file (if any) """

    file_max_attempts: Union[int, str] = ""


    has_test: bool = False
    test_rel_path: Optional[Path] = None
    """ Relative path to the ..._test.py file (or None if no file) """

    has_rem: bool = False
    rem_rel_path: Optional[Path] = None
    """ Relative path to the ...REM.md file (or None if no file) """

    has_corr: bool = False
    corr_rel_path: Optional[Path] = None
    """ Relative path to the ..._corr.py file (or None if no file) """


    corr_rem_bit_mask: int = 0
    """ Bit mask giving the configuration for correction and/or remark data
        mask&1 represent the presence of correction, mask&2 is for REM.
    """

    hdr: str = ""
    """ Python header code content """

    user_content:str = ""
    """ Python user code (only) """

    corr_content: str = ""
    """ Python solution code """

    public_tests: str = ""
    """ Public tests (only) """

    secret_tests:str = ""
    """ Code for the private tests """




    SECTION_TOKEN: ClassVar[re.Pattern] = re.compile(
        r'^(# *-+ *PYODIDE *: *\w+ *-+ *#)$', flags=re.MULTILINE
    )

    SECTION_TO_PROP: ClassVar[Dict[str,str]] = {
        ScriptSection.hdr:     "hdr",
        ScriptSection.user:    "user_content",
        ScriptSection.corr:    "corr_content",
        ScriptSection.tests:   "public_tests",
        ScriptSection.secrets: "secret_tests",
    }





    def __post_init__(self):

        self.exo_py: Optional[Path] = self.get_path_for_exo('.py')
        if not self.exo_py and self.script_name:
            raise BuildError(
                f"No python script for { self.script_name }, in { self.env.page.file.src_uri }"
            )

        script_content = read_file(self.exo_py) if self.exo_py  else ""

        # Extract everything:
        if self.SECTION_TOKEN.search(script_content):
            self.extract_multi_sections(script_content)
        else:
            self.extract_multi_files(script_content)

        self.corr_rem_bit_mask = self.has_corr + self.has_rem * 2

        # Sanity check:
        if not self.has_test and (self.has_corr or self.has_rem):
            opn,clos = '{{','}}'
            maybe_id = "" if self.id is None else f", ID={ self.id }"
            location = self.env.page.file.src_uri
            test_file = self.script_name + SiblingFile.test
            msg = (
                f'An invalid configuration of files has been found for {opn} IDE("'
                f'{self.script_name}"{ maybe_id }, ...) {clos} in the page { location }: '
                f'a correction or remark file exists but there is no { test_file } file.'
            )
            if self.env._dev_mode:
                logger.error('EXPECTED (1x) - ' + msg)
            else:
                raise BuildError(msg)


        if self.env.check_python_files:
            self.check_python()

        # self._fuuuuuusion()
        # self._cleanup_tests()



    def get_path_for_exo(self, tail:str) -> Optional[Path] :
        """ Build a sibling path fro the current page/script """
        return get_sibling_of_current_page(
            self.env, self.env.docs_dir_path, self.script_name, tail=tail
        )



    def get_path_and_existence(self, tail:str):
        """
        Return a pair (bool, Path|None), the boolean telling if some data actually exist for
        the desired tail.
        """
        path = self.get_path_for_exo(tail)
        exists = False
        content = ''
        if path:
            path = path.relative_to(CWD)
            exists = path.is_file()

            # Also checks that the file contains something, otherwise consider it absent:
            if exists:
                content = read_file(path).strip()
                exists = bool(content)
                if not exists:
                    raise BuildError(f"{path} is an empty file and should be removed.")
        return exists, path, content




    #--------------------------------------------------------------------------
    #                             MONOLITHIC WAY
    #--------------------------------------------------------------------------


    def extract_multi_sections(self, script_content:str):
        """
        Extract all the python content from one unique file with different sections:
            - HDR: header content (optional)
            - user: starting code for the user (optional)
            - corr: ... (optional - must be defined before the tests...?)
            - tests: public tests (optional)
            - secret: secret tests (optional)
        Note that the REM content has to stay in a markdown file, so that it can contain macros
        and mkdocs will still interpret those (if it were containing only markdown, it could be
        inserted on the fly by a macro, but an "inner macro call" would be ignored).
        """

        chunks = self.SECTION_TOKEN.split(script_content)
        chunks = [*filter(bool, map(str.strip, chunks))]
        pairs  = [*zip(*[iter(chunks)]*2)]


        # File structure validations:
        headers = [ self._section_extractor(section) for section in chunks
                                                     if self.SECTION_TOKEN.match(section) ]
        odds_sections = len(chunks) & 1
        duplicates    = len(headers) != len(set(headers))
        wrong_tic_toc = len(headers) != sum(
            bool(self.SECTION_TOKEN.match(header)) for header,_ in pairs
        )
        if odds_sections or duplicates or wrong_tic_toc:
            raise BuildError(f"Invalid file structure for { self.exo_py }")


        # Codes registrations:
        for section,content in pairs:
            section_name = self._section_extractor(section)
            prop = self._get_section_property(section_name)
            setattr(self, prop, content)

        self.has_corr = bool(self.corr_content)
        self.has_test = bool(self.secret_tests)
        self.has_rem, self.rem_rel_path, _ = self.get_path_and_existence(SiblingFile.rem)



    @staticmethod
    def _section_extractor(header:str):
        return header.strip(' #-').split(':')[-1].strip()


    def get_section(self, section:ScriptSection):
        """ Extract the given section """
        prop = self._get_section_property(section)
        return  getattr(self, prop)


    def _get_section_property(self, section:ScriptSection):
        if section not in self.SECTION_TO_PROP:
            raise BuildError(f'Unknown section name {section!r} in { self.exo_py }')
        return self.SECTION_TO_PROP[section]




    #--------------------------------------------------------------------------
    #                            OLD FASHION WAY
    #--------------------------------------------------------------------------


    def extract_multi_files(self, script_content:str):
        """
        "Old fashion way" extractions, with:
            - user code + public tests (+ possibly HDR) in the base script file (optional)
            - secret tests in "{script}_test.py" (optional)
            - Correction in "{script}_corr.py" (optional, but secret tests have to exist)
            - Remarks in "{script}_REM.md" (optional, but secret tests have to exist)
        """
        if script_content.startswith('#MAX'):
            logger.error(
                "Setting IDE MAX value through the file is deprecated. Move this to the IDE macro "
                f"argument.\nFile: { self.exo_py }"
            )
            script = script_content
            first_line, script = script.split("\n", 1) if "\n" in script else (script,'')

            script_content = script.strip()
            self.file_max_attempts = first_line.split("=")[1].strip()

        (
            self.hdr, self.user_content, self.public_tests,
        ) = self.env.get_hdr_and_public_contents_from(script_content)

        (
            (self.has_test, self.test_rel_path, self.secret_tests),
            (self.has_corr, self.corr_rel_path, self.corr_content),
            (self.has_rem,  self.rem_rel_path,  _),
        ) = map(self.get_path_and_existence, (
            SiblingFile.test, SiblingFile.corr, SiblingFile.rem,
        ))

        self.secret_tests = "" if not self.has_test else read_file(self.test_rel_path)




    #--------------------------------------------------------------------------
    #                            PYTHON CHECKS
    #--------------------------------------------------------------------------


    def check_python(self):
        """
        * hdr + corr + public + secret => pass
        * hdr + user + public => doesn't pass
        * hdr + user + secret => doesn't pass
        """
        if not self.script_name or self.id is not None:
            return # skip

        src    = self.get_path_for_exo('.py')
        target = Path('___XXX_check_python.py')
        target.touch(exist_ok=True)

        to_check = [
            (
                "Correction code should have passed", True, self.has_corr and self.has_test,
                [self.hdr, self.corr_content, self.public_tests, self.secret_tests],
            ),
            (
                "Initial solution should fail public tests", False, True,
                [self.hdr, self.user_content, self.public_tests],
            ),
            (
                "Initial solution should fail public + secret tests", False, self.has_test,
                [self.hdr, self.user_content, self.public_tests, self.secret_tests],
            ),
        ]
        try:
            for msg, does_run, todo, sections in to_check:

                if not todo: continue

                content = '\n\n'.join(sections)
                target.write_text(content, encoding='utf-8')
                msg += f" for { src.relative_to(CWD) }"
                kwargs = dict(shell=True, check=True, capture_output=True, timeout=2)

                if does_run:
                    try:
                        subprocess.run(f'python {target}', **kwargs)
                    except Exception as e:
                        print(e)
                        if self.env.soft_check:
                            logger.error(msg)
                        else:
                            raise BuildError(msg) from e
                else:
                    try:
                        subprocess.run(f'python {target}', **kwargs)
                        if self.env.soft_check:
                            logger.error(msg)
                        else:
                            raise BuildError(msg)
                    except: pass                    # pylint: disable=all

        finally:
            # final file cleanup
            target.unlink()






    #--------------------------------------------------------------------------
    #        PYTHON FILES MANAGEMENT IN BATCHES (used on CodEx only)
    #--------------------------------------------------------------------------



    def _fuuuuuusion(self):
        src = self.get_path_for_exo(SiblingFile.exo)
        if not src:
            return
        alter = 'fusion_tmp' / src.relative_to(self.env.docs_dir_path)
        # print(alter)
        self.__create_merged_file(alter)


    def _cleanup_tests(self):
        target_prop = 'corr_content'
        content_to_cleanup = getattr(self, target_prop)
        if self.public_tests and self.public_tests in content_to_cleanup:
            cuts = [*map(str.strip, content_to_cleanup.split(self.public_tests))]
            print(f"TESTS - {self.exo_py} : n_parts={ len(cuts) }") # | { cuts[0].strip() }")
            assert len(cuts)==2
            return

            start,end = cuts
            start = re.sub(r'(?i)# *tests?$', '', start, flags=re.MULTILINE).strip()
            setattr(self, target_prop, start+"\n"+end)

            src = self.get_path_for_exo(SiblingFile.exo)
            alter = 'fusion_tmp' / src.relative_to(self.env.docs_dir_path)
            self.__create_merged_file(alter)



    def __create_merged_file(self, merge_file:Path):
        order = [
            (section, getattr(self, self.SECTION_TO_PROP[section]))
                 for section in [
                                    ScriptSection.hdr,
                                    ScriptSection.user,
                                    ScriptSection.corr,
                                    ScriptSection.tests,
                                    ScriptSection.secrets,
                                ]]
        merged = ''.join(
            f"\n\n\n# --------- PYODIDE:{ section } --------- #\n\n{ content }"
                for section,content in order
                if content
        )

        merge_file.parent.mkdir(parents=True, exist_ok=True)
        merge_file.touch(exist_ok=True)
        merge_file.write_text(merged, encoding='utf-8')