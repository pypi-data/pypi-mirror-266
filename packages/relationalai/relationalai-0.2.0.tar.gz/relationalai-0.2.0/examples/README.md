# RelationalAI Python Examples

This folder is a self-contained project that uses `relationalai-python` in a variety of examples.

## Install

```sh
# Clone the examples locally
git clone git@github.com:RelationalAI/relationalai-python.git
cd relationalai-python/examples

# set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install -r requirements.txt
```

> :bulb: If you plan to hack on `relationalai-python` code, you can install it in editable mode to avoid having to reinstall after every modification:

```sh
cd PATH/TO/examples

# Activate the venv if you haven't already
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

pip install -e ..[dev]
```

## Running examples

> :bulb: Make sure you've got a config file in the current working directory or at ~/.rai.config before running examples. You can create one using the included CLI by running `rai init`.

Run the example file directly. For example, to run the `simple` example:

```sh
python simple.py
```

## Debugging 

@TODO: Detail the debugging experience.

```sh
# run debugger (in a separate terminal)
rai debugger
```

This will open a browser window with the debugger UI. The debugger will automatically connect to any Python process that uses the RelationalAI library in the same environment.