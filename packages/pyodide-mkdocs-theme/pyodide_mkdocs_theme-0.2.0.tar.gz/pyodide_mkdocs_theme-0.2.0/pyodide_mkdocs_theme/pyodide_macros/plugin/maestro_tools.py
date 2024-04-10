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


from typing import Any, TYPE_CHECKING

from mkdocs.config import config_options as C

if TYPE_CHECKING:
    from .pyodide_macros_plugin import PyodideMacrosPlugin



def typ_deprecated_with_custom_msg(prop:str, typ:Any):
    return C.Deprecated(
        message=f"Macros using {prop} may not work anymore. "
                "Please contact the theme author about that.",
        option_type = C.Optional(C.Type(typ)),
    )




class ConfigExtractor:
    """
    Data descriptor extracting automatically the matching property name from the mkdocs config.
    An additional path (dot separated keys/properties) can be provided, that will be prepended
    to the property name.
    """

    def __init__(self, path='', *, root='config', prop=''):
        self.root = root
        self.path = path
        self.prop = prop
        self.parent_cache = None

    def __set_name__(self, _obj, prop):
        self.prop = self.prop or prop

    def __set__(self, *a, **kw):
        raise ValueError(f"The {self.prop} property should never be reassigned")

    def __get__(self, obj:'PyodideMacrosPlugin', kls=None):
        if self.parent_cache is None:
            parent = getattr(obj, self.root)
            keys = () if not self.path else self.path.split('.')
            for key in keys:
                parent = parent[key]
            self.parent_cache = parent

        return self.parent_cache[self.prop]




class AutoCounter:
    """
    Counter with automatic increment. The internal value can be updated/rested by assignment.
    @warn: if True, the user will see a notification in the console about that counter being
    unmaintained so far (displayed once only).
    """

    def __init__(self, warn=False):
        self.cnt = 0
        self.warn_once = warn

    def __set_name__(self, _, prop:str):
        self.prop = prop        # pylint: disable=attribute-defined-outside-init

    def __set__(self, _:'PyodideMacrosPlugin', value:int):
        self.cnt = value

    def __get__(self, obj:'PyodideMacrosPlugin', __=None):
        if self.warn_once:
            self.warn_once = False
            obj.warn_unmaintained(f'The property {self.prop!r}')
        self.cnt += 1
        return self.cnt
