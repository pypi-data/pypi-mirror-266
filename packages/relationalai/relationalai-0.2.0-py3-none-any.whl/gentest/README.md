# Gentest

PyRel Tests, Testing Framework, and CLI powered by Hypothesis

## Running `gentest`

> :bulb: Installing `relationalai-python` with dev depenencies will automatically link the `gentest` CLI into your virtualenv at `.venv/bin/gentest`. If you ensure that `.venv/bin/` is on your `PATH`, you can call the command directly.

> :bulb: If you run into issues, make sure you've activated the virtualenv with `source .venv/bin/activate`.

The `gentest` CLI tool offers several sub-commands for managing and running tests:

- `test`: Run the test suite with arguments passed through to pytest.
- `watch`: Monitor for file changes and validate them in real-time.
- `encode-failure`: Encode a test failure as a base64 string for reporting.
- `reproduce`: Reproduce a failing test case from a given encoded string.
- `export`: Export utilities for debugging purposes.

To run any sub-command, use the `gentest` command followed by the name of the sub-command. For example:

```sh
gentest test
```

This will execute the test suite against `PyRel`. To see all options for a sub-command, use the `-h` or `--help` flag, e.g., `gentest test -h`.

## Interactive Development with `watch`

The `watch` subcommand automatically runs tests on file changes and offers a REPL for focused debugging:

- `target <path>` (`t`): Focuses on a single failing test, re-running only this test on changes.
- `clear` (`c`): Resets focus, affecting all tests and stopping dependent operations like `export`.
- `export` (`e`): Exports details of the currently focused failure for deeper analysis.
- `list` (`l`): Lists all failures from the last test run for a quick overview.
- `show <failure>` (`s`): Provides details on a specified failure to aid in troubleshooting.
- `quit` (`q`): Exits `gentest` and the REPL.
- `help` (`h`, `?`): Displays help text for REPL commands.

Initiate the `watch` mode with:

```sh
gentest watch
```

Use the REPL commands to streamline test debugging and quickly address failures.

## Tracking failures

We use Hypothesis' builtin failure database system for tracking discovered failures. When developing locally, these are stored in the `.hypothesis/examples` directory. The format is fairly inscrutable, but it can roughly be thought of as content hashing `<failing test fn>/<failing value>`. The files store the necessary entropy for regenerating the failing value, which can be used for quickly reproducing the failure. To grab the failing input itself, use `gentest export ir <short_path> <outfile>`. 

The gentest CLI and watch interface uses the concept of a **short path** for persistently identifying failures, which is just any valid prefix of a full failure path. For example, the failure path `a09ed02f25316759/5f25b963d90c3039` can be represented by the short path `a09ed0/5f25b9`.

Hypothesis will automatically check known failing examples before generating new ones in the regular test loop.


## Project Structure

- The `src/gentest` directory contains all of our source code.
  - `src/gentest/cli` - Implements the argument parsing and actions of the gentest CLI and watch REPL.
  - `src/gentest/harness` - Shimming, patching, and type aliases for deeper integration with Hypothesis.
  - `src/gentest/gen` - Implements hypothesis strategies for all of the `PyRel` types under test.
  - `src/gentest/validate` - Predicates used by the test suite to pass or fail generated examples (and supporting code)
- The `tests/` directory contains all of PyRel's tests.
  - `tests/roundtrip` - Contains tests that rely on roundtrip validation.
    - Tests the compiler by ensuring that any given example IR can be emitted as PyRel and unambiguously compiled back into an equivalent IR.
  

