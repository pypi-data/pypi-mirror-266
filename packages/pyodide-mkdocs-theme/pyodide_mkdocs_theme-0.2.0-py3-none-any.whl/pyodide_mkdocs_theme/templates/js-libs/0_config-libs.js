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
NOTE: Globals defined somewhere else:

    * The "ace" variable is defined in the ace library. Everything using it must be called after
      the libs step insertions.
    * CONFIG.buttonIconsDirectory (directly in main.html)
*/


const CONFIG = {

    CURRENT_REVISION: "0.1.0",

    /*
    The following values are passed from python to JS through the main.html, once this script got
    loaded. Just make sure none of those values has to be used in the libs scripts! */
    showFailedAssertionsOnValidation: null,
    encryptCorrectionsAndRems: null,
    buttonIconsDirectory: "path",
    ideProp: {},



    onDoneEvent : 'unload',         // unused, so far...

    // Various UI elements identifiers
    element: {
        searchBlock:    "div.md-search",
        dayNight:       "form.md-header__option",
        stdoutCtrlId:   "#stdout-controller-btn",
        cutFeedbackSvg: "#cut-feedback-svg",
        hourGlass:      "#header-hourglass-svg",
        qcm_admos:      ".py_mk_admonition_qcm",
        qcmInnerDiv:    ".py_mk_admonition_qcm-inner",
        qcmCounterCls:  ".qcm-counter",
        qcmWrapper:     ".qcm_wrapper",
    },

    // Auto subscriber tracking:
    subscriptionReady: {},
    subscriptionsTries: {},

    loggerOptions: {},      // jsLogger debugging config/activations


    /**Constant, to archive the terminals at runtime.
     *   - Will be garbage collected on page change or reload.
     *   - Warning if navigation.instant gets restored !!
     * */
    terms: {},   // All registered terminals


    currentScroll: undefined,       // [x,y]


    // (defined in the securedPagesData-libs.js file)
    // JS <-> python property names tracker


    cutFeedback: true,


    TESTS_TOKEN_PATTERN:    /^\s*#(\s*)test(s?)\s*$/i,
    COMMENTED_PATTERN:      /(^\s*)(\S)(.?)/,
    // HDR_TOKEN_PATTERN:   /#\s*-[\s-]*HDR\s*-[\s-]*#/i,           // not used anymore


    ACE_COLOR_THEME: {
        customTheme: undefined,
        customThemeDefaultKey: "",
        aceStyle: undefined,
    },


    feedbackShortener: {
        // StdOut:
        limit: 1000,
        head: 400,
        tail: 200,
        msg: "&lsqb;Message truncated&rsqb;",

        // Terminal stacktrace:
        traceLimit: 20,
        traceHead: 5,
        traceTail: 5,

        // Error message:
        errLimit: 15,
        errHead: 6,
        errTail: 5,
    },


    MSG: {
        successMessage:  "Terminé sans erreur !",       // reformatted later with info(...)
        runScriptPrompt: "Script lancé...",             // reformatted later with info(...)
        promptStart:     ">>> ",
        promptWait:      "... ",
        successEmojis:   ['🔥','✨','🌠','✅','🥇','🎖'],
        leftSafeSqbr:    "&lsqb;",
        rightSafeSqbr:   "&rsqb;",
        exclusionMarker: "FORBIDDEN",
        bigFail:         "\nIf You see this, there is a bug either in the website code, or in the way "
                       + "this exercice is configured.\nPlease contact the webmaster with information "
                       + "about what You were doing when this happened!\n\nDon't forget to check the "
                       + "content of the console (F12) and possibly make a screenshot of any message "
                       + "there, to help debugging.",
    },

}