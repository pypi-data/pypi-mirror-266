# Generic development instructions/tips for working on this kind of project

This project mostly uses the generic "nens-meta" setup. The idea:

- Use a virtualenv in a standard location and activate it.
- The tricky bits are pre-configured (vscode, pytest, formatting, etc).
- VScode should work out of the box.
- Commandline usage too.

(Note: this documentation was mostly generated automatically. Some project-specific instructions might be found at the end.)


## Initial python virtualenv

Virtualenvs keep your global python installation nice and clean. They also help code completion.

- Create the virtualenv in the `.venv` dir. This is a convention that's also picked up by vscode
- Activate it when working on the project.
- Install the requirements.

    $ python3 -m venv .venv --prompt nens-meta
    $ .venv/bin/activate         # <== On windows
    $ source .venv/bin/activate  # <== On linux/mac
    $ pip install -r requirements.txt

When you changed requirements, rerun the "pip install". Working on a project again after a time?: don't forget to activate again.


## Python testing

Just run:

    $ pytest

That'll discover your `test_*.py` or `*_test.py` files inside `nens_meta`.

VScode's big "run the tests" button should also automatically run it.

Just running "tox" gives you a one-stop-shop for lint, test, coverage:

    $ tox -q

This is basically what is run on github.


## Formatting + checks

If you have `ruff` installed globally you can do this:

    $ ruff format
    $ ruff check --fix

If you're using vscode with the "ruff" plugin, everything is nicely formatted and checked once you save a file. Quick and easy.

All the checks/linters are available through "tox":

    $ tox -qe lint

### Extra lines below are preserved ###
