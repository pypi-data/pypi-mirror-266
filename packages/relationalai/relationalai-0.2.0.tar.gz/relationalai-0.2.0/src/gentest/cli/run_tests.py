import pytest


def run_tests(unknown_args: list[str]|None):
    if not unknown_args:
        unknown_args = []

    pytest.main(unknown_args)
