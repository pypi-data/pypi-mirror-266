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


from urllib.parse import unquote
from pathlib import Path
from typing import Optional, Union

from .plugin.maestro_base_and_indent import BaseMaestro




PathOrStr = Union[str,Path]




def to_uri(path:Union[Path,str], *segments:str):
    """ Take a path string, potentially os dependent, and rebuild a slash separated
        version of it.
        If additional segments are given, they'll be considered new directories, up
        to a final segment that will be considered a file (hence, no trailing slash).

        Behavior for trailing separators on @path:
            - If @segments is not given, trailing separators on @path are kept (to keep
              behaviors consistent with "hidden" index.html files in mkdocs addresses
              when url_directories is True).
            - If any @segments is given, trailing separators on @path are removed
              before joining @path and @segments.
    """
    if isinstance(path,str):
        path = Path(path)
    joined = "/".join(path.parts + segments)
    joined = joined.replace('\\','/')
        # Because windows path behave weirdly when given a "root-like" path, which is
        # starting with a slash in the original string...

    if joined.startswith('//'):      # may happen on absolute paths (linux)
        joined = '/' + joined.lstrip('/')
    return joined



def get_sibling_of_current_page(
    env: BaseMaestro,
    docs_dir: Path,
    partial_path: PathOrStr,
    *,
    tail:str="",
    rel_to_docs=False
):
    """
    Extract the current page from the env, then build a path name toward a file using the
    @partial_path (string name of slash separated string, or relative Path), starting from the
    same parent directory.
    If @tail is given, it is added to the name of the last segment of of the built path.
    If @rel_to_docs is False, the result will be an absolute path of the file at documentation
    building time. If @rel_to_docs is True, the returned path will be rooted at the docs_dir,
    meaning the path will also be the valid relative path of the file on the built site.

    If @partial_path is an empty string or a Path without name, return None
    """
    path: Path = docs_dir / env.page.file.src_uri
    out_path = get_sibling(path, partial_path, tail)
    if out_path and rel_to_docs:
        return out_path.relative_to(docs_dir)
    return out_path



def get_sibling(src:Path, rel:PathOrStr, tail:str="") -> Optional[Path] :
    """ Build a sibling of the given path file, replacing the current Path.name
        with the given @rel element (path or str).
        If @tail is given, it is added to the name of the built path.
        Return None if:
            - @src has no explicit parent (using '.' on the cwd will cause troubles)
            - @rel is an empty string or is a Path without name property (empty IDE)
    """
    if not src.name or not rel or isinstance(rel,Path) and not rel.name:
        return None
    path: Path = src.parent / rel
    if tail:
        path = path.with_name( path.stem + tail )

    if not path.is_file():
        path = src.parent / 'scripts' / src.stem / rel
        if tail:
            path = path.with_name( path.stem + tail )

    return path




def read_file(target:Path) -> str:
    """
    Read the content of the given target filepath (absolute or relative to the cwd),
    NOTE: return an empty string if the path is not valid.

    Throws AssertionError if the target isn't a Path instance.
    """
    assert isinstance(target,Path), f"target should be a Path object, but was: {target!r}"
    if not target.is_file():
        return ""

    content = target.read_text(encoding="utf-8")
    return content




def convert_url_to_utf8(nom: str) -> str:
    return unquote(nom, encoding="utf-8")
