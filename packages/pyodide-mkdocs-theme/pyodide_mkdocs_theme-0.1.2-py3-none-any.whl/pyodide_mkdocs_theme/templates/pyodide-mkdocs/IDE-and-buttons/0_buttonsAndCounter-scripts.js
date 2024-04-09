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




/**Run the public tests (if any)
 * @editorName (string ): "editor_{hash}"
 * */
const play = (editorName) => withPyodideAsyncLock( async function(e){
    if(e && e.preventDefault) e.preventDefault()

    await waitForPyodideReady();
    jsLogger("[Play]")

    let [code,terminal, options] = await setupRuntimeAndTerminal(editorName);
    let stdErr=""

    try{
        stdErr = await runPythonCodeWithOptions(code, terminal, options)
    }finally{
        tearDownRuntimeAndTerminal(terminal, stdErr)
    }
    $.terminal.active().focus()

},'play')





/**Trigger the validation tests
 * @editorName (string ): "editor_{hash}"
 * */
const validate = (editorName) => withPyodideAsyncLock( async function(e){
    if(e && e.preventDefault) e.preventDefault()

    await waitForPyodideReady();
    jsLogger("[Validate]")

    let [code, terminal, options] = await setupRuntimeAndTerminal(editorName);
    let finalMsg="", stdErr=""

    try{
        // Define the user's code in the environment and run the public tests (if any)
        stdErr = await runPythonCodeWithOptions(code, terminal, options)


        // Run the validation tests only if the user's code succeeded at the previous step
        if(!stdErr){

            // If still running, run the original public tests and the secret ones...
            const publicTests = securedExtraction(editorName, CONFIG.ideProp.publicTests)
            const secretTests = securedExtraction(editorName, CONFIG.ideProp.secretTests)

            // ...unless there are no secret tests (this may happen when using KB shortcuts, while
            // there is no validation to do => just quit the testing process right away)
            if(!secretTests) return

            const autoLogAssert = securedExtraction(editorName, CONFIG.ideProp.autoLogAssert)
            options.autoLogAssert = autoLogAssert!==null ? autoLogAssert : CONFIG.showFailedAssertionsOnValidation
            options.withStdOut = false

            const fullTests = `${ publicTests }\n\n${ secretTests }`
            stdErr = await runPythonCodeWithOptions(fullTests, terminal, options)

            // On error, manage the counter of tries and the revelation of the solution, otherwise
            // reveal the solutions + setup success message (displayed in teardown step):
            if(stdErr){
                const nAttemptsLeft = updateIdeCounter(editorName)
                if(unhideSolutionAndRem(editorName, nAttemptsLeft, false)){
                    finalMsg = enhanceFailureMsg(editorName, stdErr)
                }

            }else{
                unhideSolutionAndRem(editorName)
                finalMsg = buildSuccessMessage(editorName)
            }
        }

    }finally{
        tearDownRuntimeAndTerminal(terminal, stdErr, finalMsg)
    }
    $.terminal.active().focus()

},'validate')



//-----------------------------------------------------------------------


const _generateDownloadName = (scriptName) => {
    if (scriptName!=""){
        return `${scriptName}.py`
    }
    // Handle editors without related python file:
    let [day, time] = new Date().toISOString().split("T");
    let hhmmss = time.split(".")[0].replace(/:/g, "-");
    return `script_${day}-${hhmmss}.py`;
};


/**Download the current content of the editor to the download folder of the user.
 * */
const download = (editorName) => withPyodideAsyncLock(async function(){
    await waitForPyodideReady();
    jsLogger("[Download]")

    const editor = ace.edit(editorName)
    const scriptName = editor.container.getAttribute('script_name')
    const fileName = _generateDownloadName(scriptName)
    let ideContent = editor.getValue() + ""     // enforce stringification in any case

    let link = document.createElement("a");
    let blob = new Blob([ideContent], { type: "text/plain" });
    link.href = URL.createObjectURL(blob);
    link.download = fileName

    link.click();
    URL.revokeObjectURL(link.href);
    link.remove()
    focusEditor(editorName)

},'download')



/** Upload routine (for the input that is triggered by the upload button...) */
const uploadRoutine =_=> withPyodideAsyncLock(async function() {
    await waitForPyodideReady();
    jsLogger("[Upload]")

    let number = this.id.split("_").pop();
    let idEditor = "editor_" + number;
    const uploadInput = document.getElementById("input_" + idEditor)
    uploadInput.addEventListener( "change", function (evt) {
        let file = evt.target.files[0];
        let reader = new FileReader();
        var editor = ace.edit(idEditor);
        reader.onload = function (event) {
          editor.getSession().setValue(event.target.result);
        };
        reader.readAsText(file);
      },
      false
    )
    focusEditor(idEditor)

},'upload')





//-----------------------------------------------------------------------



/**Reset the content of the editor to its initial content, and reset the localeStorage for
 * this editor on the way.
 * */
const restart = (editorName) => withPyodideAsyncLock(async function(){
    await waitForPyodideReady();
    jsLogger("[Restart]")

    const exerciseCode = getStartCode(editorName)
    applyCodeToEditorAndSave(editorName, exerciseCode)
    focusEditor(editorName)

},'restart')



/**Save the current IDE content of the user, or the given code, into the localeStorage
 * of the navigator.
 * */
const save = (editorName, exerciseCode="") => withPyodideAsyncLock(async function(){
    await waitForPyodideReady();
    jsLogger("[Save]")

    _save(editorName, exerciseCode)
    focusEditor(editorName)

},'save')

const _save = (editorName, exerciseCode="") => {
    const currentCode = exerciseCode || ace.edit(editorName).getSession().getValue()
    localStorage.setItem(editorName, currentCode);
}






//--------------------------------------------------------------------------------







/**Extract the current content of the given editor, explore it, and toggle all the lines
 * found after the `# Test` token.
 * Rules for toggling or not are:
 *      - leading spaces are ignored.
 *      - comment out if the first character is not "#".
 *      - if the first char is "#" and there is no spaces behind, uncomment.
 * */
function toggleComments(editor) {
    const codeLines = editor.getSession().getValue().split('\n')
    const iTestsToken = codeLines.findIndex(s=>CONFIG.TESTS_TOKEN_PATTERN.test(s))

    /// No tests found:
    if(iTestsToken<0) return;

    const toggled = codeLines.slice(iTestsToken+1).map(s=>{
        return s.replace(CONFIG.COMMENTED_PATTERN, (_,spaces,head,tail)=>{
            if(head=='#' && tail!=' ') return spaces+tail
            if(head!='#') return spaces+'#'+head+tail
            return _
        })
    })
    codeLines.splice(iTestsToken+1, toggled.length, ...toggled)
    const repl = codeLines.join('\n')
    applyCodeToEditorAndSave(editor, repl)
    focusEditor(editor.container.id)
  }



/**Takes in the id string of an editor, or an ACE editor as first argument, and the
 * code string to apply to it, and:
 *      - set the editor content to that string
 *      - save the code to the localeStorage
 * */
function applyCodeToEditorAndSave(editorOrName, exerciseCode){
    exerciseCode ||= "\n".repeat(6)
    const [editor, editorName]
        = typeof(editorOrName)=='string' ? [ace.edit(editorOrName), editorOrName]
                                         : [editorOrName, editorOrName.container.id]
    editor.getSession().setValue(exerciseCode);
    _save(editorName, exerciseCode)
}




const setupGlobalIdeComponentsWithTheme=(theme)=>function() {

    const jqThis = $(this)      // The #global_editor_xxx div
    const editorName = this.id.slice('global_'.length)

    const ide = jqThis.find("#"+editorName)[0]
    const aceEditor = setupAceEditor.call(ide, theme)

    const toggler = jqThis.find("[id^=comment_]")[0]
    toggler.addEventListener("click", ()=>toggleComments(aceEditor));


    jqThis.children("button").each(function(){
        const btn = $(this)
        const kind = btn.attr('btn_kind')

        let callback
        switch(kind){
            case 'play':      callback = play(editorName) ; break
            case 'validate':  callback = validate(editorName) ; break
            case 'download':  callback = download(editorName) ; break
            case 'upload':    const input=btn.children('input')[0]
                              callback = input.click.bind(input) ; break
            case 'restart':   callback = restart(editorName) ; break
            case 'save':      callback = save(editorName) ; break
            default:          throw new Error(`Y'should never get there, mate... (${ kind })`)
        }
        btn.on('click', callback)
    })

    // Initiate all terminals in the page
    jqThis.find("#term_"+editorName).each(async function(){
        const id = this.id
        await setupOrGetTerminalAndPyEnv(id)
    })
}
