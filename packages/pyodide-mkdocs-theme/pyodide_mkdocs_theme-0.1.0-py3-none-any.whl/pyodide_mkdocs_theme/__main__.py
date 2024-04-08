"""
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
"""

from argparse import ArgumentParser
from .__version__ import __version__



parser = ArgumentParser(
    'pyodide_mkdocs_theme',
    description="Scripts for pyodide-mkdocs-theme",
    epilog="""Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program comes with ABSOLUTELY NO WARRANTY."""
)
parser.add_argument(
    '-V', '--version', action='version', version=f'pyodide-mkdocs-theme {__version__}'
)
parser.add_argument(
    '-yml', action='store_true', help='Print a base configuration for the mkdocs.yml file.'
)

def main():
    args = parser.parse_args()
    print(args)

    if args.yml:
        display_yml()




def display_yml():
    print('''
# Voici un exemple presque complet de configuration pour un fichier
# mkdocs.yml utilisant pyodide-mkdocs-theme.

site_url: "{>> L'adresse de votre site web ici <<}"
site_name: "{>> Titre pour votre site <<}"
# site_description: "(optionnel)"
# repo_url: "(optionnel)"
# edit_uri: "(optionnel)"

# Copyright "CC BY-NC-SA"
copyright: |
  <p xmlns:cc="http://creativecommons.org/ns#"
  xmlns:dct="http://purl.org/dc/terms/">Partage ou adaptation possible selon les conditions de la
  licence <a
  href="http://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1"
  target="_blank" rel="license noopener noreferrer"
  style="display:inline-block;"> CC BY-NC-SA 4.0 <img
  style="height:22px!important;margin-left:3px;vertical-align:text-bottom;"
  src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img
  style="height:22px!important;margin-left:3px;vertical-align:text-bottom;"
  src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><img
  style="height:22px!important;margin-left:3px;vertical-align:text-bottom;"
  src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1"><img
  style="height:22px!important;margin-left:3px;vertical-align:text-bottom;"
  src="https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1"></a></p>


docs_dir: docs

nav:
  - "Accueil": index.md
# - ...

# Pour supprimer certains fichiers markdown de la navigation (pattern shell):
# not_in_nav: |
#   */**/*.md

theme:
  name: pyodide-mkdocs-theme

# features:
#   - navigation.instant      # Ne surtout pas activer cette option !


markdown_extensions:

  # Extensions indispensables pour le thème:
  - md_in_html              # !!REQUIS!!
  - admonition              # !!REQUIS!! Blocs colorés:  !!! info "ma remarque"
  - attr_list               # !!REQUIS!! Un peu de CSS et des attributs HTML, ex: { #id .class style="display:none" }
  - pymdownx.details        # !!REQUIS!! Admonition: ??? -> peuvent se déplier ; ???+ -> peuvent se replier.
  - pymdownx.emoji:         # !!REQUIS!! Émojis:  :boom:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - pymdownx.highlight      # !!REQUIS!! Coloration syntaxique du code
  - pymdownx.inlinehilite   # !!REQUIS!! Coloration syntaxique pour les "code spans": `#!python  code_python`
  - pymdownx.snippets:      # !!REQUIS!! Inclusion de fichiers externe.
      check_paths: true     # Fortement conseillé...
  - pymdownx.superfences    # !!REQUIS!!
  - pymdownx.arithmatex:    # !!REQUIS!!
      generic: true
  - pymdownx.striphtml:
      strip_js_on_attributes: false     # !!REQUIS!!
      strip_attributes: ""              # !!REQUIS!!


  # Extensions conseillées:
  - meta
  - abbr
  - def_list                # Les listes de définition.
  - footnotes               # Notes[^1] de bas de page.  [^1]: ma note.
  - pymdownx.caret          # Passage ^^souligné^^ ou en ^exposant^.
  - pymdownx.mark           # Passage ==surligné==.
  - pymdownx.tilde          # Passage ~~barré~~ ou en ~indice~.
  - pymdownx.tasklist:      # Cases à cocher  - [ ]  et - [x]
      custom_checkbox: false
      clickable_checkbox: true
  - pymdownx.tabbed:        # Volets glissants:  === "Mon volet"
      alternate_style: true # Meilleure compatibilité pour mobiles
      slugify: !!python/object/apply:pymdownx.slugs.slugify
        kwds:
          case: lower
  - pymdownx.keys           # Touches du clavier:  ++ctrl+d++
  - toc:
      toc_depth: 0          # Si vous voulez supprimer la ToC (table of content) de la page


# Configuration minimale pour les plugins
plugins:
  - awesome-pages:          # Pas indispensable, mais... (pip install mkdocs-awesome-pages-plugin)
      collapse_single_pages: true

  - material/search         # Les plugins de material-mkdocs doivent être préfixés!

  - exclude:                # (pip install mkdocs-exclude)
      glob:                 # Patterns identifiant des pages à ne pas inclure dans le build.
        - sous_dossier/**/*REM.md   # Les fichiers de remarques DOIVENT être exclus
        - sous_dossier/**/*.py      # Les fichiers python DOIVENT être exclus

  - exclude-search:         # (pip install mkdocs-exclude-search)
      exclude:              # Pour les fichiers inclus dans le build, que la recherche ne doit pas indexer
        - bac_a_sable.md

  - pyodide_macros          # !!REQUIS!!


validation:                 # Si mkdocs est lancé en mode strict (mkdocs ... --strict), les warnings lèveront une erreur
  omitted_files: warn
  unrecognized_links: warn

''')



if __name__ == '__main__':
    main()
