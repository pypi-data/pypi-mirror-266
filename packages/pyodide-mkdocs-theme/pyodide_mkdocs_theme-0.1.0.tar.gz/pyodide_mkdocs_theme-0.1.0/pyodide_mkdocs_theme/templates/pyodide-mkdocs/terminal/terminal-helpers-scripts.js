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


/**Given a terminal id, focus the corresponding jQuery.terminal and send it back to the caller.
 * */
const getTerminal=termId=>{
    $(termId).focus()
    return $.terminal.active()
}


/**Given a terminal id string, extract the corresponding ACE editor name, if it exists.
 * If the terminal is a "stand alone" version, return empty string instead.
 * */
const getCorrespondingEditorId=termId=>{
    if(termId.startsWith('term_only')){
        return ""
    }
    const editorName = termId.slice("term_".length)
    return editorName
}



/**Build a jQuery terminal and bind it to the underlying pyodide runtime.
 * The @termId argument is a html/css id string, without the leading hashtag.
 * */
const buildInteractiveTerminalSession = termId => {
    const jqTermId = '#'+termId

    const editorName = getCorrespondingEditorId(termId)
    const bindings = {
        "CTRL+C": keyboardInterruptReport(pyFuncs.clear_console),
        ...(!editorName ? {} : {
                'CTRL+I': _ => toggleComments(ace.edit(editorName)) || false,
                'CTRL+S': play(editorName),
                'CTRL+ENTER': validate(editorName),
            })
    }

    // Create and inject the terminal object in the DOM
    const interpreterWithLock = withPyodideAsyncLock(
        cmdLineInterpreter(editorName,jqTermId), 'terminal'
    )
    const term_options = {
        greetings: "",              // pyconsole.banner(),
        prompt: CONFIG.MSG.promptStart,
        completionEscape: false,
        keymap: bindings,
        onBlur: function(){},  // Allow to leave the textarea, focus-wise. DO NOT PUT ANY CODE INSIDE...
        completion: function (command, callback) {
            callback(pyFuncs.pyconsole.complete(command).toJs()[0]);    // autocompletion
        },
    }
    const terminal = $(jqTermId).terminal(interpreterWithLock, term_options)
    return terminal
}






/**Terminal interpreter function.
 * Can work command by command, of using groups of lines, when the user is pasting multiline
 * codes in the terminal.
 */
const cmdLineInterpreter = (editorName, jqTermId) =>{
    let term, options

    return async function(command) {
        if(!options){
            term = getTerminal(jqTermId)
            options = buildOptionsForPyodideRun(
                editorName, {runCodeAsync: commandRunnerAsync(term)}
            )
        }
        term.pause();
        try{
            await runPythonCodeWithOptions(command, term, options)
        }finally{
            // Release the terminal to the user:
            term.resume();
            await sleep();    // Enforce the UI update, going through the next tick
        }
    }
}



const commandRunnerAsync = (term) => async function(command){

    // multiline commands should be split (useful when pasting)
    for (let c of command.split("\n")) {

        let future = pyFuncs.pyconsole.push(c);

        // set the beginning of the next line in the terminal:
        const isIncompleteExpr = future.syntax_check=="incomplete"
        const headLine = isIncompleteExpr ? CONFIG.MSG.promptWait : CONFIG.MSG.promptStart
        term.set_prompt(headLine);

        switch (future.syntax_check) {
            case "complete":
                try {
                    await pyFuncs.await_fut(future);
                } finally {
                    future.destroy()
                }
            case "incomplete":
                continue    // complete also goes there...
            case "syntax-error":
                term.error(future.formatted_error.trimEnd());
                continue
            default:
                throw new Error(`Unexpected state ${future.syntax_check}`);
        }
    }
}







/** Transfer the Ctrl+C event from JS to python, currying the python console clearing function.
 *  NOTE: this is actually totally useless, until workers are used...
 * */
const keyboardInterruptReport = (clear_console) => async function(_event){
    if (!getSelectionText()) {
        const terminal = $.terminal.active()
        let currentCmd = terminal.get_command();
        clear_console();
        terminal.echo(CONFIG.MSG.promptStart + currentCmd);
        terminal.echo(error("KeyboardInterrupt"));
        terminal.set_command("");
        terminal.set_prompt(CONFIG.MSG.promptStart);
    }
}




// Code issued from https://stackoverflow.com/questions/5379120/get-the-highlighted-selected-text
function getSelectionText() {
    let text = "";
    if(window.getSelection) {
        text = window.getSelection().toString();

    }else if(document.selection && document.selection.type != "Control") {
        text = document.selection.createRange().text;
    }
    return text;
}