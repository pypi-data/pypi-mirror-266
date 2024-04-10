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

/**Decorator like factory function, managing the global pyodide lock.
 * If a call is done while pyodide is locked, it is delayed until the lock is available.
 * */
var withPyodideAsyncLock=(function(){

    /**Everything is run async but single threaded, so a global lock can be added, using a simple
     * boolean flag...
     * */
    let pyodideLocked = false

    return function(asyncCallback, name=""){
        const logName = asyncCallback.name||name

        const wrapper = async function(...args){
            jsLogger("[LOCK?] -", logName, pyodideLocked)
            while(pyodideLocked){
                await sleep(100)
            }
            jsLogger("[LOCK ACQUIRE] -", logName)
            pyodideLocked = true
            let ret;
            try{
                ret = await asyncCallback.apply(this,args)
            }finally{
                pyodideLocked = false
                jsLogger("[LOCK RELEASE] -", logName)
            }
            return ret
        }
        return wrapper
    }
})()





/**Auto-subscription routine to document changes.
 * If the subscription is not possible yet (readyForSubscription[waitOn] is falsy), try again
 * @delay later until it works.
 *
 * @waitId :  Property to observe in readyForSubscription global object.Also used as subscription
 *            identifier.
 * @callback: Routine to run when the document changes
 * @options : An object with optional fields:
 *      .delay (=50): Time interval (in ms) to wait in between two subscription attempts.
 *      .now (=false): If true, ignore the CONFIG.subscriptionReady property and subscribe at call
 *              time. If false, a callback will be returned by the `subscribeWhenReady` function,
 *              that the caller can use to signal when the subscription is ready.
 *      .waitFor (=null): If given, it must be a boolean provider or a jquery identifier string,
 *              which will result in a function checking for the existence of that element in
 *              the DOM. This function will be called every .delay ms and the subscription will
 *              be delayed until it returns true. This has precedence over the .now option.
 *
 * @throws: Error if more than 20 subscriptions attempts are done without success.
 * */
function subscribeWhenReady(waitId, callback, options={}){

    let {now, delay, waitFor} = {
        delay: 50,
        now: false,
        waitFor: null,
        ...options
    }

    now = now && !waitFor                       // has to wait if waitFor is used
    CONFIG.subscriptionReady[waitId] = now

    const checkReady = !waitFor                  ? ()=>null
                     : typeof(waitFor)=='string' ? ()=>{ CONFIG.subscriptionReady[waitId] = $(waitFor).length>0 }
                                                 : ()=>{ CONFIG.subscriptionReady[waitId] = waitFor() }
    const isNotReady =()=>{
        checkReady()
        return !CONFIG.subscriptionReady[waitId] || !globalThis.document$
    }

    function autoSubscribe(){

        if(isNotReady()){
            const nTries = CONFIG.subscriptionsTries[waitId]+1 || 1
            if(nTries==20){
                throw new Error(`Impossible to subscribe to ${ waitId } in time: too many tries.`)
            }
            CONFIG.subscriptionsTries[waitId] = nTries
            setTimeout(autoSubscribe, delay)

        }else{
            jsLogger('[Subscribing] -', waitId)
            const subscript = document$.subscribe(callback)
            document.addEventListener(CONFIG.onDoneEvent, function(){
                jsLogger("[Unsubscribing] -", waitId)
                subscript.unsubscribe()
            })
        }
    }

    autoSubscribe()

    if(!now) return ()=>{ CONFIG.subscriptionReady[waitId]=true }
}







/**Square brackets in "rich text format" must be escaped, otherwise they are messing up the
 * terminal formatting informations
 * */
const escapeSquareBrackets=msg=>{
    return msg.replace(/\[/g, CONFIG.MSG.leftSafeSqbr)
              .replace(/\]/g, CONFIG.MSG.rightSafeSqbr)
}


/**Formatting factory function, for messages used in the jquery terminal.
 * */
function richTextFormat(content, style, color="", background="") {
    content = escapeSquareBrackets(content)
    return `[[${ style };${ color };${ background }]${ content }]`;
}

let error   = (content) => richTextFormat(content, "b", "red");
let warning = (content) => richTextFormat(content, "", "orange");
let stress  = (content) => richTextFormat(content, "b");
let info    = (content) => richTextFormat(content, "i", "grey");
let italic  = (content) => richTextFormat(content, "i");

CONFIG.MSG.successMessage = info(CONFIG.MSG.successMessage)
CONFIG.MSG.runScriptPrompt = info(CONFIG.MSG.runScriptPrompt)





/**Takes a string and cut the "middle chunk" of them if it is considered too long (length > 1750),
 * shortening it in the following way:
 *   - keep the 500 first and 300 last chars
 *   - replace the middle with a message
 * */
function textShortener(text){
    if(CONFIG.cutFeedback && text.length > CONFIG.feedbackShortener.limit){
        const head = text.slice(0,CONFIG.feedbackShortener.head)
        const tail = text.slice(-CONFIG.feedbackShortener.tail)
        text = `${ head }\n...\n${ CONFIG.feedbackShortener.msg }\n...\n${ tail }`
    }
    return text
}



/**Create a button with tooltip, just like the python _html_builder one.
 * */
function buttonWithTooltip(options, content){
    options = {
        buttonId: "",
        shift: 50,          // %
        fontSize: 1.5,      // em
        tipWidth: 15,       // em
        tipText: "",
        ...options
    }
    const buttonId = !options.buttonId ? "" : `id="${ options.buttonId }" `
    return `
<button ${ buttonId }class="tooltip header-btn" type="button"
 style="--tool_shift:${ options.shift }%; font-size:${ options.fontSize }em;">
    <span class="tooltiptext" style="width:${ options.tipWidth }em;">${ options.tipText }</span>
    ${ content }
</button>
`
}



/**Randomly pick a value from an array.
 * @throws Error if the array is empty.
 * */
function choice(arr){
    if(!arr.length){
        throw new Error("Cannot pick from an empty array")
    }
    const i = Math.random() * arr.length | 0
    return arr[i]
}




/**Async sleep (time given in milliseconds / must be awaited by the caller)
 * */
function sleep(ms=0) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
