/*
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
*/

/*
** This docstring is automatically updated at build time, from build_tools.py **
** This way, it's always in synch with pages_editors_configs.py:IdeConfig **

Inserted on the fly in each page needing IDEs (done by the macros_ide).
The structure of this object is the following:

var PAGE_IDES_CONFIG = {
    "editor_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx: {
        attempts_left: int = 0      # Not overwriting this means there is no counter displayed
        auto_log_assert: bool=None  # If None, use the global setting, CONFIG.showFailedAssertionsOnValidation
        hdr_content: str = ""       # HDR part of "exo.py"
        user_content: str = ""      # Non-HDR part of "exo.py" (initial code)
        corr_content: str = ""      # content of "exo_corr.py"
        public_tests: str = ""      # test part of "exo.py" (initial code)
        secret_tests: str = ""      # Content of "exo_test.py" (private tests)
        corr_rem_config: int = 0    # Bit mask:   has_corr=corr_rem_config&1 ; has_rem=corr_rem_config&2
        encrypted: bool = True      # Tells if the html content is still encrypted or not
        rec_limit: int = -1         # recursion depth to use at runtime, if defined (-1 otherwise).
        excluded: List[str]=None    # List of forbidden instructions (functions or packages)
        excluded_methods: List[str]=None # List of forbidden methods accesses
        white_list: List[str]=None  # White list of packages to preload at runtime
    }
}
*/

/**To make the code independent of the python definitions */
CONFIG.ideProp = {
    // Actually never used, but kept here for internal code validation checks
    corrContent:    "corr_content",

    attemptsLeft:   "attempts_left",
    autoLogAssert:  "auto_log_assert",
    corrRemMask:    "corr_rem_config",
    encrypted:      "encrypted",
    excluded:       "excluded",
    excludedMethods:"excluded_methods",
    hdrContent:     "hdr_content",
    publicTests:    "public_tests",
    recLimit:       "rec_limit",
    secretTests:    "secret_tests",
    userContent:    "user_content",
    whiteList:      "white_list",
}


/**Extract some data for the given editor reference, checking that the prop is valid on the way.
 * Use the property names defined in the IDE_CONFIG object.
 * */
function securedExtraction(editorName, prop){
    const editorData = _checkPageData(editorName, prop)
    return editorData[prop]
}


/**Update some data for the given editor reference, checking that the prop is valid on the way
 * Use the property names defined in the IDE_CONFIG object.
 * */
function securedUpdate(editorName, prop, data){
    const editorData = _checkPageData(editorName, prop)
    editorData[ prop ] = data
}


/**Extract a value fr the given IDE, making sure the property name is correct.
 * */
function _checkPageData(editorName, prop){
    const editorData = PAGE_IDES_CONFIG[ editorName ]
    const out = editorData && editorData[ prop ]
    if(!editorData || out===undefined){
        throw new Error(
            `Couldn't find data for PAGE_IDES_CONFIG.${ editorName }["${ prop }"].`
            +( editorData ? '' : `\n"${ editorName }" is not a key.` )
        )
    }
    return editorData
}


/**Build the initial code content for an editor (initia user function + public tests).
 * */
function getStartCode(editorName){
    const userCode = securedExtraction(editorName, CONFIG.ideProp.userContent)
    const publicTests = securedExtraction(editorName, CONFIG.ideProp.publicTests)
    const exerciseCode = [userCode, publicTests].filter(Boolean).join('\n\n\n# Tests\n\n\n') + "\n"
    return exerciseCode
}
