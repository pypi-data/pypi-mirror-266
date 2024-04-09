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

""" Parsing and modifications logistic. """

from mkdocs.exceptions import BuildError




def replace_chunk(source:str, start:str, end:str, repl:str, *, at=0, keep_limiters=False):
    """ Given a @source and two delimiters/tokens, @start and @end, find those two tokens in
        @source, then replace the content of source between those two tokens with @repl.

        @at=0:                  Starting point for the search of @start in @source.
        @keep_limiters=False:   If True, the @start and @end tokens are kept and @repl is
                                placed in between them instead.
    """
    i,j = eat(source, start, at)
    _,j = eat(source, end,   j)
    if keep_limiters:
        repl = start + repl + end
    return source[:i] + repl + source[j:]



def eat(source:str, token:str, start=0, *, skip_error=False):
    """ Given a @source text, search for the given @token and returns the indexes locations
        of it, i and j (i: starting index, j: ending index, exclusive, as for slicing).

        @start=0:           Starting index for the search
        @skip_error=False:  Raises ValueError if False and the token isn't found.
                            If True and the token isn't found, returns i=j=len(source).
    """
    i = source.find(token, start)
    if i>=0:
        return i, i+len(token)

    if skip_error:
        return len(source), len(source)

    # handle error message:
    end  = min(1000, len(source)-start)
    tail = "" if end != 1000 else ' [...]'
    raise ValueError(f"Couldn't find {token=} in:\n\t[...] {source[start:end]}{ tail }")





def encrypt_string(text, key = 43960):
    """ Applique c ^ 43960 à chaque caractère de text (43960 = 0b1010101010101010) and send that
        as dot joined integers (needed to allow JS to decode emojis "the way python sees them")
        (...sort of...)
    """
    return ".".join( f"{ ord(c) ^ key :0>5}" for c in text )




def build_code_fence(
    content:str,
    indent:str="",
    line_nums=1,
    lang:str='python',
    title:str=""
) -> str :
    """
    Build a markdown code fence for the given content and the given language.
    If a title is given, it is inserted automatically.
    If linenums is falsy, no line numbers are included.
    If @indent is given each line is automatically indented.

    @content (str): code content of the code block
    @indent (str): extra left indentation to add on each line
    @line_nums (=1): if falsy, no line numbers will be added to the code block. Otherwise, use
                     the given int value as starting line number.
    @lang (="python"): language to use to format the resulting code block.
    @title: title for the code block, if given. Note: the title cannot contain quotes `"`
    """
    line_nums = f'linenums="{ line_nums }"' if line_nums else ""
    if title:
        if '"' in title:
            raise BuildError(
                f'Cannot create a code fence template with a title containing quotes:\n'
                f"  {lang=}, {title=!r}\n"
                f"{content}"
            )
        title = f'"{ title }"'

    lst = [
        '',
        f"```{ lang } { title } { line_nums }",
        *content.strip('\n').splitlines(),
        "```",
        '',
    ]
    out = '\n'.join( indent+line for line in lst )
    return out
