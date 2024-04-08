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


/**Initiate or retrieve a jquery terminal instance.
 *
 * If the terminal doesn't exist yet, this function does:
 *  - create a jQuery terminal, dedicated to one IDE
 *  - bind it to the python environment
 *  - setup the python environment and the pyodide one
 *
 * Note that the terminal is stored in a global variable, so that the next call from the
 * same IDE will actually return the same object instead of creating a new one.
 *
 * On the other hand, the python environment setup will be defined again, in case the user
 * messed with it (wanted or not).
 *
 * @returns: the active jQuery terminal
 */
async function setupOrGetTerminalAndPyEnv(termId, focus=false) {

    // Make sure nothing can be done until the pyodide environment is ready:
    await waitForPyodideReady();
    setCurrentScroll()

    let isCreation = true
    let term;

    // Short circuit if already exists!
    if(CONFIG.terms[termId]){
        jsLogger("[Terminal] - Retrieve "+termId)

        isCreation = false
        term = CONFIG.terms[termId]
        if(focus) term.focus()
        term.clear()            // Reset content
        await sleep(200)        // Delay for the user to see the change

    }else{
        jsLogger("[Terminal] - Initiate "+termId)

        // Create the jQuery terminal, then bind the python stdout/err:
        term = buildInteractiveTerminalSession(termId)
    }

    setupAdditionalPythonEnvironmentFeatures()

    CONFIG.terms[termId] = term;
        // ...To avoid garbage collection? (apparently not!!)
        // But useful to avoid creating a new one on the next execution...!

    // Enforce vertical scroll position by focusing on the #py_mk_pin_scroll_input
    jsLogger("[Terminal] - isCreation && !focus =", isCreation && !focus)
    if(isCreation && !focus) restoreScrollPositionAndBlur()

    return term
}





/**Add recursion limiter features to the python environment.
 * */
const setupAdditionalPythonEnvironmentFeatures=(options={})=>{

    options = {
        exclusionsTools: true,
        inputPrompt: true,
        version: true,
        ...options
    };
    Object.entries(options).forEach(([opt,todo])=>{
        jsLogger("[Feature (re-/load)] -", opt)
        if(todo) pyodide.runPython(featureCode(opt))
    })
}





/**Function injected into the python environment (must be defined earlier than others
 * to be used in the tweaked import function)
 * */
function inputWithPrompt(text) {
    let result = prompt(text);
    $.terminal.active().echo(result);
    return result;
}


function getFeedbackConfig(){
    return CONFIG.cutFeedback
}


const featureCode=(option)=>{

    switch(option){

        case "inputPrompt":
            return `
def _hack():
    import js
    __builtins__.input = js.inputWithPrompt
_hack()
del _hack
`


        case "version":
            return `
def version():
    print("${stress("Pyodide-MkDocs")} : version ${error(CONFIG.CURRENT_REVISION)}")`



        case "exclusionsTools":
            return `
def _hack():

    def move_forward(stuff):
        treasure = __builtins__.__builtins___
        if type(stuff) is str and stuff in treasure:
            return treasure[stuff][0]

    class ExclusionError(Exception):
        @staticmethod
        def throw(that:str):
            raise ExclusionError(f"${ CONFIG.MSG.exclusionMarker }: don't use {that}")

    __builtins__.move_forward = move_forward
    __builtins__.ExclusionError = ExclusionError

_hack()
del _hack
`

        default:
            throw new Error(`Unknown feature: ${option}`)
    }
}
