"""
Pyodide-MkDocs-Theme is a theme for MkDocs that allows building websites integrating, on the client side:

- IDEs (code editor),
- Interactive Python consoles,
- An online judge for testing user-written functions, associated with corrections and remarks,
- And some other features (qcms, ...).

## Guarantees:

    - No cookies
    - No registration
    - Created by teachers for teachers

This project is a redesign of the prototype [`pyodide-mkdocs`](https://bouillotvincent.gitlab.io/pyodide-mkdocs/) initially created by [Vincent Bouillot](https://gitlab.com/bouillotvincent/).

## How it works:

The technology enabling this feat is called [Pyodide](https://pyodide.org/en/stable/). It is associated with JavaScript elements, such as [jquery.terminal](https://terminal.jcubic.pl/api_reference.php) and [ACE Editor](https://ace.c9.io/).

Pyodide uses WebAssembly to bridge between Python and JavaScript and provide an environment for manipulating the JavaScript DOM with Python, or vice versa for manipulating Python from JavaScript.


## Links:

* [GitLab repository](https://gitlab.com/frederic-zinelli/pyodide-mkdocs-theme)
* [Documentation](http://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/) (french only)



![IDE capture example](http://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/assets/pyodide-mkdocs-theme-ex.png)

"""

