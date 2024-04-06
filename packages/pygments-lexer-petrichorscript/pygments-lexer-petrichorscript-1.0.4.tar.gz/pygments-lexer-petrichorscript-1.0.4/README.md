Custom Pygments RegexLexer for [Petrichor Script](https://github.com/sparklitwizzl/petrichor).

Distributed under AEL-NC-AT 1.1 (see LICENSE file).

Install via PyPi: `pip install pygments-lexer-petrichorscript`

Install via GitHub branch: `pip install https://github.com/sparklitwizzl/pygments-lexer-petrichorscript/archive/main.zip`

This will install Pygments if not already installed.


Use with MkDocs on Windows:

1. Navigate to your MkDocs root directory.
2. Run `py -m venv [virtual environment folder name]`
3. Make sure the virtual environment is running.
4. Install the lexer from the source of your choice.
5. Run `mkdocs build`. With any luck, the custom lexer will be incorporated into the built output.
6. If using `mike` for versioning, run `mike deploy`. MAKE SURE TO DO THE PREVIOUS STEP FIRST, OR THE CUSTOM LEXER WONT BE USED.
