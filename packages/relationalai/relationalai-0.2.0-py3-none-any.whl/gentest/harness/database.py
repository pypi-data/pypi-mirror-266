import os
from typing import Callable
from hypothesis.database import _hash, DirectoryBasedExampleDatabase
from hypothesis.internal.reflection import function_digest
from gentest.harness.vendor_types import HypothesisTestFn
from gentest.util import PROJECT_DIR


HYPO_DB_PATH = os.path.join(os.path.dirname(PROJECT_DIR), ".hypothesis", "examples")

HYPO_DB = DirectoryBasedExampleDatabase(HYPO_DB_PATH)
KEY_LEN = 8
VAL_LEN = 10

def get_test_hash(test_fn: Callable|HypothesisTestFn):
    if hasattr(test_fn, "is_hypothesis_test"):
        return get_test_inner_hash(test_fn.hypothesis.inner_test)
    raise Exception("Must pass a valid hypothesis test fn to get its key. Did you mean to pass the inner fn to `get_test_inner_key()`?")


def get_test_inner_hash(test_inner_fn: Callable):
    return _hash(function_digest(test_inner_fn))

def get_value_hash(value: bytes):
    return _hash(value)

def get_short_path(key_hash: str, value_hash: str):
    return f"{key_hash[:KEY_LEN]}/{value_hash[:VAL_LEN]}"

def expand_short_key(short_key: str, db_path: str):
    if not os.path.isdir(db_path):
        raise Exception("No hypothesis database detected.")

    keys = os.listdir(db_path)
    key = None
    for cur_key in keys:
        if cur_key.startswith(short_key):
            if key is not None:
                raise Exception("Hash collision! Specify a longer segment of the key hash.")
            key = cur_key

    if key:
        return key
    else:
        raise Exception(f"Invalid test key hash: '{short_key}'")

def expand_short_value(key: str, short_value: str, db_path: str):
    key_path = os.path.join(db_path, key)
    if not os.path.isdir(key_path):
        raise Exception(f"No directory found for key '{key}'.")

    values = os.listdir(key_path)
    value = None
    for cur_value in values:
        if cur_value.startswith(short_value):
            if value is not None:
                raise Exception("Hash collision! Specify a longer segment of the value hash.")
            value = cur_value

    if value:
        return value
    else:
        raise Exception(f"Invalid repro input value hash: '{short_value}'")

# Function to retrieve a particular failing input by hash ID
def expand_short_path(short_path: str, db_path: str = HYPO_DB_PATH, relative = False):
    (short_key, short_value) = short_path.split("/")
    if not short_key or not short_value:
        raise Exception("Malformed repro short path. It should be in the form <key_hash>/<value_hash>")

    key = expand_short_key(short_key, db_path)
    value = expand_short_value(key, short_value, db_path)

    if relative:
        return os.path.join(key, value)
    else:
        return os.path.join(db_path, key, value)

def get_conjecture_data(file_path: str):
    with open(file_path, "rb") as file:
        conjecture_data = file.read()
        return conjecture_data
