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



/**Given an editorName, automatically build the default options to pass as argument to the
 * runPythonCodeWithOptions function.
 *
 * The content of the config optional argument will override any basic option, except for
 * the packagesAliases object, where the config.packagesAliases entries will be added.
 *
 * @returns: an options object, described as follow:
 *     @options :
 *          .autoLogAssert:   (boolean) If true, will automatically add the code of a failing
 *                            assertion as its message if it doesn't have one already.
 *          .excluded:        (String[]) Instructions to exclude at runtime.
 *          .excludedMethods: (String[]) Methods calls to exclude at runtime (string containment).
 *          .packagesAliases: (Record<string,string>) mapping of imports that should be aliased
 *                            automatically for the user, if they try to import them.
 *          .recLimit:        (number) recursion depth (or -1 if not used)
 *          .runCodeAsync:    async python code runner.
 *          .withStdOut:      (boolean) Display the content of the stdOut or not.
 *          .whiteList:       (Array of strings) list of modules to import before the code
 *                            restrictions are put in place for the user's code.
 *
 * WARNING: If the editorName argument isn't given or is falsy, the fields excluded, whiteList
 *          and recLimit are not included.
 * */
const buildOptionsForPyodideRun=(editorName='', config={})=>{
    const options = {
        autoLogAssert: true,        // default for the PUBLIC tests...
        excluded: [],
        excludedMethods: [],
        recLimit: -1,
        runCodeAsync: async(code)=>pyodide.runPython(code),
        withStdOut: true,           // default for the PUBLIC tests...
        whiteList: [],
    }
    if(editorName){
        OPTIONS_TO_EXTRACT.forEach( js_prop =>{
            options[js_prop] = securedExtraction(editorName, CONFIG.ideProp[js_prop])
        })
    }
    return {
        ...options,
        ...config,
        packagesAliases: {
            // turtle: "pyo_js_turtle",         // this never got finished => unusable.
            ...config.packagesAliases||{}
        },
    }
}

const OPTIONS_TO_EXTRACT = [
    'excluded',
    'excludedMethods',
    'whiteList',
    'recLimit',
]





/**Special JS Error: methods calls exclusions are tested from the JS runtime, instead of pyodide.
 * So, JS has to throw a special error that will mimic ("enough"...) the pattern of pyodide errors
 * and hance, will be considered legit errors.
 */
class PythonError extends Error {
    toString(){ return "Python" + super.toString() }
}





/**Takes a code as argument, and run it in the pyodide environment, using various options:
 *
 * @throws: Any JS runtime Error, if something went very wrong... (python errors are swallowed
 *          and just printed in the terminal)
 * @returns: The stdErr formatted string message that got printed in the terminal, or empty
 *           string if no error.
 *           Note that the message is displayed in the console already, so this is only a
 *           "marker" to propagate some logic in other parts of the application.
 *
 * NOTE:
 *    - Pyodide itself is using eval, so replacing globally the builtin will cause a lot of
 *      troubles and just won't work.
 *    - This function doesn't take in charge the pyodide environment setup, (preparation,
 *      rebuilding the setup, ...).
 *    - On the other hand it DOES take in charge installation of missing modules/packages.
 */
async function runPythonCodeWithOptions(code, terminal, options){

    try{
        // Do first the methods exclusions check, to gain some time (avoids loading modules if
        // the error would show up anyway after loading them)
        const nope = options.excludedMethods.filter(methodCall=>code.includes(methodCall))
        if(nope.length){
            const plural = nope.length>1 ? "s":""
            const nopes = nope.map( s=>s.slice(1) ).join(', ')
            const msg = `${ CONFIG.MSG.exclusionMarker } method${plural}: ${ nopes }`
            throw new PythonError(msg)
        }

        // Detect possible user imports and install the packages to allow their imports:
        await installAndImportMissingModules(code, options)

    }catch(err){
        const strErr = generateErrorLog(err, code)
        terminal.echo(strErr);
        return strErr
    }

    const withExclusions = options.excluded.length>0 || options.recLimit > 0

    // Setup stdout capture. WARNING: this must always be done even if it's not shown to the user.
    // If not done, a previous execution might have close the StringIO and if ever the user prints
    // something, it would result in an error without that:
    setupStdIO()

    // Setup code/imports exclusions if any (later id better)
    if(withExclusions) setupExclusions(options.excluded, options.recLimit)

    let stdErr="", stdOut="", delayedErr
    try {
        await options.runCodeAsync(code)
    }catch(err){
        // Since generateErrorLog might run python code, the exclusions must be removed _before_
        // the function is called, so store the error for later use.
        delayedErr = err

    } finally {
        // Teardown steps must always occur, whatever happened (even for JS errors), hence in a
        // finally close, and they also must be protected against failure, so in their own
        // try/catch/finally construct:
        try {
            if(withExclusions) restoreOriginalFunctions(options.excluded)

            // Now only, compute the error message if needed.
            if(delayedErr){
                stdErr = generateErrorLog(delayedErr, code, options.autoLogAssert)
            }

            // Always extract the stdout and close the buffer (avoid memory leaks)
            let captured = getFullStdIO() || ""

            // Send stdout feedback to the user only if allowed:
            if(options.withStdOut){
                stdOut = escapeSquareBrackets( textShortener(captured) )
            }

        }catch(err){
            // This second catch is there so that the user can see the JS error in the terminal.
            // (Note: maybe I should actually throw them again...?)
            stdErr = generateErrorLog(err, code)

        } finally {
            const someMsg = stdOut + stdErr
            if(someMsg){
                terminal.echo(someMsg);
            }
            return stdErr
        }
    }
}


/*
------------------------------------------------------------------
                       Imports logistic
------------------------------------------------------------------
*/


/**Explore the user's code to find missing modules to install. If some are found, load micropip
 * (if not done yet), then install all the missing modules.
 * Also import all the packages present in options.whiteList.
 *
 * @code : the user's code
 * @options :Same as `runPythonCodeWithOptions`
 * */
const installAndImportMissingModules = async function(code, options){

    const pkgReplacements = options.packagesAliases
    const whiteList = options.whiteList

    // Things to import whatever happens:
    const preImport = whiteList.map(name=>'import '+name)

    const wantedModules = getUserImportedModules(code)
    const installedModules = getAvailablePackages()
    const missing = wantedModules.filter(
        name => !installedModules.includes(name) && !options.excluded.includes(name)
    )

    if(missing.length){
        await pyodide.loadPackage("micropip");
        let micropip = pyodide.pyimport("micropip");

        for(let name of missing){
            if(name in pkgReplacements){
                preImport.push(`import ${ pkgReplacements[name] } as ${ name }`)
                name = pkgReplacements[name]
            }
            jsLogger("[Micropip] - Install", name)
            await micropip.install(name);
        }
    }

    // Import everything that is needed (either because module aliasing or because the code
    // restrictions would forbid it later):
    pyodide.runPython(preImport.join('\n'))
}



/**Rely on pyodide to analyze the code content and find the imports the user is trying to use.
 * */
const getUserImportedModules=(code)=>{
    return pyodide.runPython(`
    def _hack():
        from pyodide.code import find_imports
        __builtins__.imported_modules = find_imports(${JSON.stringify(code)})
    _hack()
    del _hack
    __builtins__.imported_modules
    `);
}


/**Extract all the packages names currently available in pyodide.
 * */
const getAvailablePackages=()=>{
    return pyodide.runPython(`
    def _hack():
        import sys
        __builtins__.loaded_modules = " ".join(sys.modules.keys())
    _hack()
    del _hack
    __builtins__.loaded_modules
    `
    ).split(' ')
}




/*
------------------------------------------------------------------
        Manage python standard out redirection in terminal
------------------------------------------------------------------
*/


/**Use a StringIO stdout, so that the full content can be extracted later
 * */
const setupStdIO =_=> pyodide.runPython(`
    def _hack():
        import sys, io
        sys.stdout = io.StringIO()
    _hack()
    del _hack
`)

const getFullStdIO =_=> pyodide.runPython(`
    def _hack():
        import sys
        __builtins__._stdout = sys.stdout.getvalue()
        sys.stdout.close()

    _hack()
    del _hack
    __builtins__._stdout
`)




/*
------------------------------------------------------------------
                      Manage code exclusions
------------------------------------------------------------------
*/



/**Put in place code exclusions. Are handled:
 *   - builtin function calls
 *   - imports
 *   - method calls (done through a simple string check in the code, in runPythonCodeWithOptions)
 *
 *
 * ## RATIONALS:
 *
 * To forbid the use of some functions or packages, replace them in the global scope by "functions"
 * that look "more or less the same", but will raise an error when called, or when used in the
 * wrong way (imports).
 *
 *
 * ## PROBLEMS:
 *
 * 1. Pyodide itself uses various functions to run python code:
 *      - eval is used in pyodide.runPython
 *      - reversed and/or min and/or max may be used when building a stacktrace when an error is
 *        thrown in python
 * 2. This forbids to replace the __builtins__ versions of those functions (see about imports)
 * 3. but the __main__ script is run separately of pyodide actual "python runtime".
 *
 *
 * ## SOLUTION FOR BUILTINS FUNCTIONS:
 *
 * - Redeclare forbidden things in the global scope, through `globals()`, using an object that will
 *   systematically throw an ExclusionError when it's called.
 * - Since those are in the global scope, they are visible through `dir()`, so add some make up on
 *   those, using a class that redefines its __qualname__ and __repr__, so that it's less obvious
 *   they are the anticheats (it will still remain obvious for those who know enough, but if they
 *   can find about that, they probably could solve the problem the right way anyway).
 * - The (hidden) function `move_forward('builtin_name')` can be used in the tests to get back the
 *   original builtin. If used, it must be done inside a closure, so that the original builtin
 *   doesn't override the "Raiser" in the global scope (see below).
 * - Pyodide runtime won't see those globals, so it is not affected in any way. Only the user's or
 *   tester's codes are.
 * - Since the hacked version are available to the user in the global runtime, they could just
 *   delete them to get back the access to the original  __builtins__ version. To limit this risk,
 *   an extra check is done after the user's code has been run, verifying that the hacked function
 *    is still defined in the global scope, and that it's still the original Raiser instance.
 *
 *
 * ## SOLUTION FOR IMPORTS
 *
 * The main problem about `import` is that it actually go directly through `__builtins__`, using
 * `__import__`. So in that case, there is no other choice than hacking directly the __builtins__,
 * and then put it back in place when not useful anymore.
 *
 *
 * ## RECUSION LIMIT
 *
 * The sys module function is directly hacked, then put back in place: meaning, the function
 * setrecursionlimit is replaced at user's rutnime with a Raiser object. 
 *
 * */
const setupExclusions =(excluded, recLimit)=>{
    // Store None in the __builtins___ dict for things that aren't builtin functions, aka, names 
    // of forbidden module.

    /** WARNING!
     *  Keep in mind that the code of the Raiser instances will run "in context". 
     *  This means it will be subject to existing exclusions, so it must never use a function that
     *  could be forbidden. Possibly...
     *  Force this reason, copies of all the butilins used in the Raiser code are stored locally,
     *  to be sure the Raiser won't use Raiser instances... XD
     * */
    const code = `
    def _hack():

        class Raiser:
            __name__ = __qualname__ = 'function'

            def __init__(self, key):  self.key = key

            def __repr__(self): return f"<built-in function {self.key}>"

            def __call__(self, *a, **kw):
                key = self.key

                head = a and base_isinstance(a[0],base_str) and a[0].split(".")[0]

                is_forbidden = (
                    key != '__import__' or
                    key == '__import__' and head in dct
                )
                if is_forbidden:
                    that = key if key!='__import__' else head
                    raise ExclusionError.throw(that)

                # if reaching this point, the call is a valid import, so apply it:
                return base_import(*a,**kw)


        # Store the originals used here to avoid troubles with exclusions at runtime:
        base_import = __import__
        base_str = str
        base_isinstance = isinstance

        __builtins__.__builtins___ = dct = {}
        raiser_import = Raiser('__import__')
        dct['__import__'] = [base_import, raiser_import]
        __builtins__.__import__ = raiser_import


        for key in ${ JSON.stringify(excluded) }:
            stuff = getattr(__builtins__, key, None)
            dct[key] = [stuff, None]
            # => the dict will store [None,None] for module names

        if ${ recLimit } != -1:
            import sys
            sys.setrecursionlimit(${ recLimit })
            dct['setrecursionlimit'] = [sys.setrecursionlimit, None]

        for key,lst in dct.items():
            stuff = lst[0]
            if callable(stuff) and key!='__import__':       # import already handled
                globals()[key] = lst[1] = Raiser(key)
                # store the reference to the raiser, to check against it later

    _hack()
    del _hack `

    // console.log(code)

    pyodide.runPython(code)
}




/**Cancel the code exclusions (done as soon as possible, to restore pyodide's normal behaviors).
 * */
const restoreOriginalFunctions =exclusions=>{
    pyodide.runPython(`
    def _hack():
        G = globals()

        not_ok = any(
            key for key,(func,raiser) in __builtins___.items()
                if raiser is not None and key!='__import__' and raiser is not G.get(key)
        )
        if not_ok:
            ExclusionError.throw("${ exclusions }")

        for key,(func,raiser) in __builtins___.items():

            if key == '__import__':
                __builtins__.__import__ = func

            elif func is not None:
                G[key] = func
                if key == 'setrecursionlimit':
                    func(1000)
    _hack()
    del _hack
    `)
}