# Design

Modify the `cli` function in `src/mistune/__main__.py` to handle the `--output -` option by sending the result to stdout instead of writing to a file.

## Architecture fit

This change will be made in the CLI module, which is responsible for handling command-line arguments and outputting results.

## File and symbol plan

- `src/mistune/__main__.py` · `cli` (edit) — Modify the `cli` function to check if the `--output` option is set to `-`. If so, send the result to stdout using `sys.stdout.write` instead of writing to a file.

## Test approach

Add a new test case to `tests/test_cli.py` to verify that the `--output -` option sends the result to stdout.
