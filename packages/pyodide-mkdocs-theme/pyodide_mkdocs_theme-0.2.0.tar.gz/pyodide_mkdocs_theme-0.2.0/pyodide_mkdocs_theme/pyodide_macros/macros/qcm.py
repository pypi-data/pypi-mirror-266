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

import re
from functools import wraps
from textwrap import dedent
from typing import Any, List, Optional

from mkdocs.exceptions import BuildError

from ..plugin.maestro_extras import MaestroExtras
from ..paths_utils import get_sibling_of_current_page
from ..tools_and_constants import HtmlClass







def true_false_none_for(v:Optional[bool], truthy:Any, falsy:Any, none=""):
    """
    Depending on the value of the first argument, return the corresponding choice,
    truthy, falsy or none.
    """
    return none if v is None else truthy if v else falsy











def multi_qcm(env:MaestroExtras):
    """
    @inputs:          lists of data for one question, aka:
                        - question title
                        - list of choices
                        - list of correct answers
                        - kwargs, for single=Optional[bool]  >>>  spec not fixed yet...
    @shuffle=False:   Questions and their items are shuffled on each refresh/retry
    @hide=False:      Correct answers will stay hidden if True after checking the user's answers
    @admo_kind="!!!": Control the kind of admonition used for the QCM
    @admo_type='tip': Category of admonition to use
    @qcm_title=None:  Title for the admonition. If not given "Question" (possibly plural) is used.

    @ID:int=None:     To disambiguate GCMs macro calls if needed
    @DEBUG=False:     If True, md output will be printed to the console
    """

    @wraps(multi_qcm)
    def wrapped(
        *inputs,
        shuffle:bool=False,
        hide:bool=False,
        multi:Optional[bool]=None,
        admo_kind:str="!!!",
        admo_class:str="tip",
        qcm_title:str=None,
        ID:Optional[int]=None,
        DEBUG:bool=False,
    ):
        """
        WARNING:    extra closing </p> tags needed here and there to guarantee the
                    final html structure!

        Reasons:
        1. THE MD RENDERER GENERATES INVALID HTML, WHEN MIXING html+md PERIOD!
        2. the md renderer will automatically open a <p> tag when starting the admo content
        3. If _ever_ the user defines a multiline content anywhere in the qcm, a new <p>
            tag will be started, leaving the previous one hanging in the air...
        4. So far, so good...: the html is invalid, but rendered correctely/usable.
        5. CATACLYSM: use another plugin that will pass that html to the BSoup...:
            depending on the html parser used, Beautif(o)ulSoup _WILL_ generate the missing
            closing tags, and this will entirely mess up the actual html.

        So, to avoid this, the extra closing `</p>` are added. They _LOOK_ lke they are
        hanging, but they will actually produce valid html.
        """

        def qcm_start():
            qcm_id = env.get_qcm_id()

            admo_classes = ' '.join(kls for kls in [
                HtmlClass.py_mk_admonition_qcm,
                HtmlClass.qcm_shuffle * shuffle,
                HtmlClass.qcm_hidden * hide,
                true_false_none_for(multi, HtmlClass.qcm_multi, HtmlClass.qcm_single),
                qcm_id,
            ] if kls )

            plural = "s" * (len(questions_data) > 1)
            admo_title = f'Question{plural}' if qcm_title is None else qcm_title
            opening = f'{ indent }{ admo_kind } { admo_class } { admo_classes } "{ admo_title }"'
            return [
                opening,
                '',         # KEEP!
                auto_indent('\n</p KEEP><ol>\n'),
            ]

        def qcm_close():
            admonition_lst.append(auto_indent("</p KEEP></ol>"))


        def question_open(
            admonition_lst:list, question:str, n:int, lst_answers:List[int], default_multi
        ):
            is_multi = len(lst_answers) > 1
            multi_kls = true_false_none_for(
                is_multi or default_multi,
                HtmlClass.qcm_multi,
                HtmlClass.qcm_single,
            )
            answers = ','.join(map(str,lst_answers))
            tag_open = f'</p KEEP><li class="{ multi_kls }" correct="{ answers }" markdown>\n{ question }'
            admonition_lst.append(auto_indent(tag_open))

        def question_close():
            admonition_lst.append(auto_indent("</li>\n"))
            # Extra linefeed for presentational purpose only (DEBUG=True): it doesn't have any
            # impact anymore, since everything inside a qcm is inserted through "<tag markdown>".


        def question_options(admonition_lst:list, items):
            """ Always use "md_in_html" approach, to simplify the construction. It is required
                anyway when the first item starts with a code block...
            """
            admonition_lst.append(auto_indent('</p KEEP><ul>'))
            admonition_lst.extend(
                auto_indent(item, wrap_li=True) for item in items
            )
            admonition_lst.append(auto_indent("</ul>"))


        def validate_question_config(question, items, lst_correct, multi):

            duplicates = len(lst_correct) != len(set(lst_correct))
            unknown    = set(lst_correct) - set(range(1,1+len(items)))
            if duplicates or unknown:
                raise BuildError(
                    f"Correct answers are invalid for question:\n{question}\nAnswers: {lst_correct}"
                )

            # validate "multi" aspect, but without actually updating the value (see multi_kls)
            # (...that's probably a bad idea...?)
            if len(lst_correct)==1 and multi is None:
                raise BuildError(
                    "Found a QCM question with only one valid answer, while no information was "
                    "available to know is it is a multi- or single choice question.\nPlease set "
                    "the `multi` argument either on the current `corr_qcm` macro call, or on the "
                    "parent `def_qcm` macro call (if you already did that, the structure the "
                    f"markdown in the document is probably incorrect).\n\nQuestion:\n{ question }"
                )

        #------------------------------------------------------------------


        if len(inputs)==1 and isinstance(inputs[0], str):
            inputs = extract_csv_file(env, inputs[0])

        # Unify data, adding/extracting systematically the extra_dct element:
        questions_data = [
            [
                qcm_format(q),
                [*map(qcm_format,items)],
                ans,
                dct[0] if dct else {}
            ]
            for q,items,ans,*dct in inputs
        ]

        id_pattern = "" if ID is None else rf".*?,\s*ID\s*=\s*{ ID }\b\s*"
        call_pattern = re.compile(rf"multi_qcm[(]{ id_pattern }")
        indent = env.get_indent_in_current_page(call_pattern)
        auto_indent = auto_indenter_factory(indent)

        admonition_lst = qcm_start()

        for n, (question, items, lst_answers, extra_dct) in enumerate(questions_data, 1):

            is_multi = extra_dct.get('multi', multi) if extra_dct else multi
            validate_question_config(question, items, lst_answers, is_multi)

            question_open(admonition_lst, question, n, lst_answers, is_multi)
            question_options(admonition_lst, items)
            question_close()

        qcm_close()


        output = '\n'.join(admonition_lst)
        output = f'\n\n{ output }\n\n'    # Enforce empty spaces around in the markdown admonition

        if DEBUG:
            print(output)
        return output

    return wrapped








def auto_indenter_factory(indent:str):
    """ Auto-indenter factory """

    def indenter(content:str, wrap_li=False, lvl:int=1):
        """
        Takes a @content, possibly multiline, and indent all lines (including the first) with the
        base @indent and an extra @lvl, where each level counts for 4 space characters.

        If @is_item is True, handle the "li" element appropriately, meaning:
            - prepend with "* " for simple content
            - surround the item with `<li markdown>...</li> if it's a code bloc`
        """
        current_indent = f"{ indent }{ 4*lvl * ' ' }"
        if wrap_li:
            content = f'<li markdown="1">\n{ content }\n</li>'
        return current_indent + content.replace('\n',"\n"+current_indent)

    return indenter




def qcm_format(msg:str):
    """ Use the natural/minimal indentation and strip spaces on both ends """
    bare = dedent(msg).strip()
    return bare





#---------------------------------------------------------------------------------



QUOTES = "'‘“\""


def extract_csv_file(env:MaestroExtras, input_file, sep=";") -> List[str] :
    """ Extract info from external file, to build a multi qcm """

    def csv_entry_to_qcm_input(entry:dict):
        question = entry["Question"]
        list_answers = [entry[key] for key in entry if "Answer" in key and entry[key] is not None]
        list_correct = list(map(int, entry["Valid"].split(",")))
        dictionnaire_var = to_dict(entry["Variable"]) if entry["Variable"] is not None else None
        return [question, list_answers, list_correct, dictionnaire_var]

    def to_dict(string:str):
        string = string + ","
        dico = {}
        regex = r"\s*(\w*)\s*:\s*(\[[\s\w,\.'\"‘“’”]*\]|\w*)\s*,"
        words: List[str] = re.findall(regex, string)
        for var in words:
            dico[var[0]] = list(map(convert_type, var[1].strip("[").strip("]").split(",")))
        return dico

    def convert_type(string:str):
        string = string.strip()
        if string[0] in QUOTES:
            return str(string[1:-1])
        elif "." in string:
            return float(string)
        else:
            return int(string)

    #------------------------------------------------------------------

    cvs_target = get_sibling_of_current_page(env, env.docs_dir_path, input_file)     # NON TESTÉ

    if not cvs_target or not cvs_target.is_file():
        return []

    csv_file = []
    file_content = cvs_target.read_text(encoding="utf-8")
    content = file_content.splitlines()
    header = content.pop(0).split(sep)
    for ligne in content:
        split_ligne = ligne.split(sep)
        dico = {
            header[i]: split_ligne[i].replace("\\\\", "\\") if split_ligne[i] != "" else None
            for i in range(len(header))
        }
        csv_file.append(dico)

    inputs = tuple(map(csv_entry_to_qcm_input, csv_file))
    return inputs
