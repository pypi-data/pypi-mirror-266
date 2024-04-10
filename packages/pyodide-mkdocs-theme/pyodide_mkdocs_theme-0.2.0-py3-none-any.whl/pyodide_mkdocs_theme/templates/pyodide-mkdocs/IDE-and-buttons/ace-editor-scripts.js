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


function createAceThemes(){

    const getRGBChannels=colorString=>[
        colorString.slice(1, 3), colorString.slice(3, 5), colorString.slice(5, 7),
    ].map(s=>parseInt(s,16));


    const bodyStyles = window.getComputedStyle(document.body);
    const primaryColor = bodyStyles.getPropertyValue("--md-primary-fg-color");

    document.documentElement.style.setProperty(
        "--main-color", getRGBChannels(primaryColor)
    );

    const _slate = document.getElementById("ace_palette").dataset.aceDarkMode;
    const _default = document.getElementById("ace_palette").dataset.aceLightMode;
    let [default_ace_style, customLightTheme] = _default.split("|")
    let [slate_ace_style,   customDarkTheme] = _slate.split("|")
    customLightTheme ||= "default"
    customDarkTheme  ||= "slate"

    // Correspondance between the custom and the classic palettes
    CONFIG.ACE_COLOR_THEME.customThemeDefaultKey = customLightTheme
    CONFIG.ACE_COLOR_THEME.customTheme = {
        [customLightTheme]: "default",
        [customDarkTheme]: "slate",
    };

    // Get ACE style
    CONFIG.ACE_COLOR_THEME.aceStyle = {
        default: default_ace_style,
        slate: slate_ace_style,
    };
}


function getTheme() {
    // automatically load current palette
    const palette = __md_get("__palette")
    let curPalette = palette===null ? CONFIG.ACE_COLOR_THEME.customThemeDefaultKey
                                    : palette.color["scheme"]

    const style = CONFIG.ACE_COLOR_THEME.customTheme[curPalette]
    return "ace/theme/" + CONFIG.ACE_COLOR_THEME.aceStyle[style];
}



/**Create an ACE editor for one IDE.
 * */
function createACE_IDE(editorName, exerciseCode, ideMaximumSize, isV) {
    jsLogger('[createACE_IDE] - '+editorName)

    ace.require("ace/ext/language_tools");      // TODO: ty moving that in the global setup?

    const options = {
        // https://github.com/ajaxorg/ace/blob/092b70c9e35f1b7aeb927925d89cb0264480d409/lib/ace/autocomplete.js#L545
        autoScrollEditorIntoView: false,
        copyWithEmptySelection: true,       // active alt+flèches pour déplacer une ligne, aussi
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: false,
        enableSnippets: true,
        tabSize: 4,
        useSoftTabs: true,                  // 4 spaces instead of tabs
        navigateWithinSoftTabs: false,      // this _fucking_ actually "Atomic Soft Tabs"...
        printMargin: false,                 // hide ugly margins...
        maxLines: ideMaximumSize,
        minLines: isV ? ideMaximumSize : 6,
        mode: "ace/mode/python",
        theme: getTheme(),
    }
    const editor = ace.edit(editorName, options);

    editor.commands.bindKey(
        { win: "Ctrl-Space", mac: "Cmd-Space" },
        "startAutocomplete"
    )
    editor.commands.addCommand({
        name: "commentTests",
        bindKey: { win: "Ctrl-I", mac: "Cmd-I" },
        exec: (editor)=>toggleComments(editor),
    })
    editor.commands.addCommand({
        name: "runPublicTests",
        bindKey: { win: "Ctrl-S", mac: "Cmd-S" },
        exec: play(editorName),
    })
    editor.commands.addCommand({
        name: "runValidationTests",
        bindKey: { win: "Ctrl-Enter", mac: "Cmd-Enter" },
        exec: validate(editorName),
    })

    applyCodeToEditorAndSave(editor, exerciseCode)
    editor.resize();
}



/** Following blocks paint the IDE according to the mkdocs light/dark mode
 * */
function paintAllAces() {
    jsLogger("[Paint_ACEs]")

    let theme = getTheme();
    for (let theEditor of document.querySelectorAll('div[id^="editor_"]')) {
        let editor = ace.edit(theEditor.id);
        editor.setTheme(theme);
        editor.getSession().setMode("ace/mode/python");
    }
}



/**Initialize one the ACE editor of one "ide" component, injecting the actual ACE component
 * in the related placeholder in the DOM.
 * */
function setupAceEditor(theme) {
    const ideMaximumSize = this.getAttribute('max_size')
    const isV = this.getAttribute('is_v')=='true'

    // Try to restore a previous session, or extract default starting code:
    let exerciseCode = localStorage.getItem(this.id) || getStartCode(this.id)

    // Create the Ace editor (id=`#${ this.id }`) with the initial content.
    createACE_IDE(this.id, exerciseCode, ideMaximumSize, isV)

    // Extract the freshly created ACE editor...
    let editor = ace.edit(this.id);

    // Extract its current height and enforce the value on the terminal if isV is true. This has
    // to be done on next tick, so that editor.container.style.height has been actually applied.
    if(isV){
        setTimeout(() => {
            const height = this.style.height
            const term_div = $(`#global_${ this.id } .term_editor_v`)
            term_div.css("height",height)
        });
    }

    editor.setTheme(theme);
    editor.getSession().setMode("ace/mode/python");

    // Editor content is saved every 25 keystrokes
    let nChange = 0;
    editor.addEventListener("input", function () {
        if(nChange++ % 25 == 0) _save(this.id)
    })
    return editor
}




/**Automatically gives the focus to the ACE editor with the given id
 * */
function focusEditor(editorName){
    ace.edit(editorName).focus()
}