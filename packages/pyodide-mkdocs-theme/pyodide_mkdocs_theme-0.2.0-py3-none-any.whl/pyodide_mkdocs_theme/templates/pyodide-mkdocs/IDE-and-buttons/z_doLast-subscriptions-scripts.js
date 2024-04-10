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


// Gather color theme data (once only)
createAceThemes()



// Setup reactivity around the day/night button
document
  .querySelector("[data-md-color-scheme]")
  .addEventListener("change", () => paintAllAces());

// This would be better, but the active line in dark mode doesn't work as intended anymore...
// $("form.data-md-component").on("change", paintAllAces)



// Setup actions to perform each time the document has changed (page load)

subscribeWhenReady('SetupIDEs', function(){
  jsLogger("[SetupIDEs]")

  // Initialize the content of each IDE in the page
  const theme = getTheme()
  $("[id^=global_editor_]").each(setupGlobalIdeComponentsWithTheme(theme))

  // Setup the input related to each upload button of the IDEs:
  $("[id^=input_editor_]").each(uploadRoutine());

}, {now: true})



// /**Debugging purpose only */
// function checkTerms(){
//   $("[id^=term_editor_]").each(function(){
//     console.log('height', $(this).css('margin'), $(this).css('padding'))
//   })
// }
// checkTerms()