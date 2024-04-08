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


from mkdocs.config.base import Config
from mkdocs.config import config_options as C

from mkdocs_macros.plugin import MacrosPlugin
from .maestro_tools import typ_deprecated_with_custom_msg







# Verify if something changed on the MacrosPlugin side... (moved to on_startup)

_EXPECTED_MACRO_CONF = set("""
module_name
modules
render_by_default
include_dir
include_yaml
j2_block_start_string
j2_block_end_string
j2_variable_start_string
j2_variable_end_string
on_undefined
on_error_fail
verbose
""".strip().splitlines())

_SRC_MACROS_CONF = dict(MacrosPlugin.config_scheme)

_MISSING_MACROS_PLUGIN_PROPS = _EXPECTED_MACRO_CONF - set(_SRC_MACROS_CONF)
MISSING_MACROS_PROPS = (
    "" if not _MISSING_MACROS_PLUGIN_PROPS else "\nDisappeared from MacrosPlugin:" + ''.join(
        f'\n\t{name}' for name in _MISSING_MACROS_PLUGIN_PROPS
    )
)

_NEW_MACROS_PLUGIN_PROPS = set(_SRC_MACROS_CONF) - _EXPECTED_MACRO_CONF
EXTRAS_MACROS_PROPS = (
    "" if not _NEW_MACROS_PLUGIN_PROPS else "\nNew config in MacrosPlugin:" + ''.join(
        f'\n\t{name}' for name in _NEW_MACROS_PLUGIN_PROPS
    )
)


J2_STRING                   = _SRC_MACROS_CONF['include_dir'].default
DEFAULT_MODULE_NAME         = _SRC_MACROS_CONF['module_name'].default
DEFAULT_UNDEFINED_BEHAVIOR  = _SRC_MACROS_CONF['on_undefined'].default







class OtherConfig(Config):
    """ Options used in the macros that have not been updated yet """

    scripts_url = typ_deprecated_with_custom_msg('scripts_url', str)
    site_root   = typ_deprecated_with_custom_msg('site_root', str)




# Only defines the values exposed to the user in mkdocs.yml.
# When a property is declared here, don't forgot to add the related extractor on the
# BaseMaestro class.
class PyodideMacrosConfig(Config):
    """
    Configuration for the main pyodide-mkdocs-theme plugin.
    """

    others = C.SubConfig(OtherConfig)


    show_code_on_failed_assertions = C.Type(bool, default=True)
    """
    When an assertion fails in the secret tests and that assertion doesn't have any assertion
    message, the code of the assertion itself will be displayed in the terminal if this option
    is set to True (default).
    This behavior is global, but can be overridden on a "per IDE" base, using the `auto_log_assert`
    optional argument.
    """

    skip_py_md_paths_names_validation = C.Type(bool, default=False)
    """
    By default, the path names of all the `.py` and `.md` files present in the docs_dir are checked
    so that they do not contain any character other than letters, digits, dot or dash. This
    ensure the IDE related macros will properly work.
    If unwanted characters are found, a BuildError is raised. Setting this flag to True will bypass
    this verification.
    """

    check_python_files = C.Type(bool, default=False)
    """
    If True, the different sections of the python files will be tested against each others during
    the build and provide feedback in the console.
    Unless the `soft_check` option is used, a BuildError will be raised if something considered
    wrong happen. See the documentation for more details.

    NOTE:
        - This is totally independent from the pyodide environment so, for example, it won't give
          a warning if a forbidden function is used in the tests (which will fail on the website).
        - The verifications considerably increase the build time (expect something around  x10).
    """

    soft_check = C.Type(bool, default=True)
    """
    If True and the python sections are verified, the build won't be interrupted if something wrong
    or suspicious is discovered and only a message in the console will be displayed.
    """


    load_yaml_encoding = C.Type(str, default='utf-8')
    """
    Encoding to use when loading yaml data from the original MacrosPlugin.
    (The original method doesn't use any encoding argument, which can lead to different behaviors
    between Windows and Linux (typically: during a pipeline!).
    """


    encrypt_corrections_and_rems = C.Type(bool, default=True)
    """
    Define if the html tags containing the correction and remarks have to be encrypted or not when
    building the website. Passing this to False can be useful during development, but value should
    _ALWAYS_ be set to true on the deployed website: keep in mind the search engine can otherwise
    dig out content of those while the user is searching for something else.
    """


    macros_with_indents = C.Type(str, default='')
    """
    Allow to register external macros that will use the `PyodideMacrosPlugin.get_indent` logistic
    to insert indented multiline contents in the page.
    `macro_with_indents` is a space separated string of all the names of the macros to register.
    """

    show_indent_errors = C.Type(bool, default=False)
    """
    If True, all errors related to indentation logistic for macros are bypassed and a message is
    printed in the console instead.
    The purpose of this option is _not_ to deactivate the securities, but to allow gathering info
    about all the problems at once: note that the resulting markdown content will most likely be
    incorrect and rendered the wrong way.
    """

    ignore_macros_plugin_diffs = C.Type(bool, default=False)
    """
    If True, no error will be raised when checking the configuration of the macros plugin against
    the one of pyodide-macros. Note that if this error is raised, the build probably won't succeed
    or the output will probably be buggy.
    """


    _dev_mode = C.Type(bool, default=False)
    """ Run the plugin in development mode (don't use that...) """


    # ---------------------------------------------------------------------------------------
    # Replication of MacrosPlugin options (merging the config_scheme properties programmatically
    # is not enough, unfortunately...)


    module_name              = C.Type(str,  default=DEFAULT_MODULE_NAME)
    modules                  = C.Type(list, default=[])
    render_by_default        = C.Type(bool, default=True)
    include_dir              = C.Type(str,  default=J2_STRING)
    include_yaml             = C.Type(list, default=[])
    on_error_fail            = C.Type(bool, default=False)
    verbose                  = C.Type(bool, default=False)

    j2_block_start_string    = C.Type(str,  default=J2_STRING)
    j2_block_end_string      = C.Type(str,  default=J2_STRING)
    j2_variable_start_string = C.Type(str,  default=J2_STRING)
    j2_variable_end_string   = C.Type(str,  default=J2_STRING)
    on_undefined             = C.Type(str,  default=DEFAULT_UNDEFINED_BEHAVIOR)
