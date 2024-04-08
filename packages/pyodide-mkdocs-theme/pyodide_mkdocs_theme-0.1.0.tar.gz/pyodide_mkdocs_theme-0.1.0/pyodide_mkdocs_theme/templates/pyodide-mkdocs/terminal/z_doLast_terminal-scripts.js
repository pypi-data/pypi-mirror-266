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

subscribeWhenReady(
    'SetupLoneTerms',
    function(){
        jsLogger("[SetupLoneTerms]")

        // Setup independent terminals, if any
        $("div[id^=term_only_]").each(async function(){
            const id = this.id
            await setupOrGetTerminalAndPyEnv(id)
        })
    },
    {now: true}
)



subscribeWhenReady('SetupStdoutBtns', function(){
    jsLogger("[SetupStdoutBtns]")

    const xRays = [...$(".stdout-x-ray-svg")].map(x=>$(x))

    $(".stdout-ctrl").each(function(){
        const jThis = $(this)
        jThis.on('click', function(){
            CONFIG.cutFeedback = !CONFIG.cutFeedback
            const method = CONFIG.cutFeedback ? 'removeClass': 'addClass'
            xRays.forEach(x=>x[method]('py_mk_hidden'))
        })
    })
  }, {now: true}
)
