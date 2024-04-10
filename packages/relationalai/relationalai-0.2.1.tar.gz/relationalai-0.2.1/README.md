# The RelationalAI Python Library

This repo contains PyRel, the Python library for RelationalAI.

## Example

```python
import relationalai as rai

model = rai.Model("People")
Person = model.Type("Person")
Adult = model.Type("Adult")

with model.rule():
    Person.add(name="Joe", age=74)
    Person.add(name="Bob", age=40)
    Person.add(name="Jane", age=10)

with model.rule():
    p = Person()
    p.age >= 18
    p.set(Adult)

with model.query() as select:
    a = Adult()
    z = select(a, a.name, a.age)

print("People!\n")
print(z.results)
```

## Links
- [Getting Started](https://github.com/RelationalAI/relationalai-python/blob/main/docs/getting_started.md)
- [Video Demo](https://relationalai.slack.com/archives/C0652R3806T/p1699899660005289)
- [AT&T Demo (using Jupyter and graph vis!)](https://relationalai.slack.com/archives/C0652R3806T/p1702493565063899)

> :bulb: Want to try PyRel right away? Check out [`examples/`](./examples) for a ready-made project with a variety of usage samples.

## Install

### Quick Start

```bash
pip install relationalai
```

### Full Guide

The instructions below will guide you through setting up a new project with PyRel using Python's built-in virtual environment package `venv`.

First, make sure you have Python (3.10, 3.11, or 3.12) and `pip` available from your command line. You can check this by running `python --version`.

To create a PyRel project, make a folder and navigate to it in your terminal. Then create a virtual environment and install the `relationalai` package using these commands:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install relationalai
```

Create a config file using the included CLI:

```bash
rai init
```

You will be prompted to choose between Snowflake or Azure; more detailed instructions regarding those options and how to find the credentials you need for them are available [here](./docs/api_reference/configuration/).

> :bulb: You can inspect the state of your configuration setup with `rai config:explain`.

To build graph queries and rules in your project, create and run a Python file with the following contents:

```python
import relationalai as rai

model = rai.Model("MyFirstModel")
Movie = model.Type("Movie")

# Add some movies to the model
with model.rule():
    Movie.add(title="The Mummy")
    Movie.add(title="The Mummy Returns")
    Movie.add(title="George of the Jungle")

# Retrieve data from the model to use in python
with model.query() as select:
    movie = Movie()
    results = select(movie, movie.title)

# Results are a dataframe, use any library or function you like to work with them.
print(results)
```

Documentation is available in the [`docs/`](./docs) directory.
For more examples, see [`examples/`](./examples).


# Contributing

## Installation for Contributors

> :warning: Ensure you're in a virtual environment to isolate dependencies and avoid hard-to-diagnose conflicts.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

Install `relationalai-python` in editable mode with the dev dependencies included.

```bash
pip install -e '.[dev]'
```

## Testing

See [`tests/end2end`](./tests/end2end/).


## New Releases

To create a new release for PyPI, do the following:

1. Update the version number in `pyproject.toml` and commit to `main`.
2. Go to https://github.com/RelationalAI/relationalai-python/releases/new and create a new release with the same version number. You can create a new tag here with the "Choose a tag" dropdown. The version indicator should be in the format `vX.Y.Z`.
3. Fill in the release title (just the version number again) and description (a summary of the changes).
4. Click "Publish release".

That's it. A GitHub Action will automatically build and publish the new release to PyPI.

## Linting

You can lint using `ruff check` (assuming you've activated the virtual environment; otherwise `.venv/bin/ruff check`). You can also use `ruff check --fix` to attempt to fix the issues.

### Lint on Save

If you want to automatically lint your Python files on save, you can install the `Run on Save` extension by `emeraldwalk` and add the following configuration to a file called `.vscode/settings.json` in the project directory:

```json
{
    "emeraldwalk.runonsave": {
        "commands": [
            {
                "match": ".*\\.py$",
                "cmd": "${workspaceFolder}/.venv/bin/ruff check --fix ${file}",
                "isAsync": true
            }
        ]
    }
}
```

### Pre-commit Hook

You can also do this as a pre-commit hook (so that a lint check happens when you commit rather than when you save the file). To do this, add the following to a file called `.git/hooks/pre-commit` in the project directory:

```bash
#!/bin/sh

.venv/bin/ruff check $(git diff --cached --name-only --diff-filter=d | grep '\.py$')
```

Then do `chmod +x .git/hooks/pre-commit` to make the file executable.

Then if you attempt to make a commit with a Python file that doesn't pass the linting checks, the commit will be rejected. You can then do `ruff check --fix` to attempt to fix the issues.

## Building a Wheel

If you need to build a wheel for the package, you can do so with the following command:

```bash
python -m build
```

The resulting wheel and tarball will be in the `dist` directory.