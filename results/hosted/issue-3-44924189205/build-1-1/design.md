# Design

Edit the `_output` function in `src/mistune/__main__.py` to handle the `--output -` option by sending output to stdout instead of writing to a file.

## Architecture fit

The change will be made in the `__main__.py` file, which is responsible for handling command-line arguments and invoking the appropriate functions. The `_output` function will be modified to check if the output file is `-` and, if so, use `sys.stdout` instead of opening a file.

## File and symbol plan

- `src/mistune/__main__.py` · `_output` (edit) — Modify the `_output` function to check if the output file is `-` and, if so, use `sys.stdout` instead of opening a file.

## Test approach

Add unit tests in `tests/test_main.py` to verify that the `--output -` option correctly sends output to stdout and that other filenames still work as expected.
