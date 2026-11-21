# Design

Modify the `_output` function in `src/mistune/__main__.py` to handle the `--output -` and `-o -` options by sending the result to stdout instead of writing to a file.

## Architecture fit

This change adheres to the constraints by not altering the token contract, extending through the plugin system, and respecting the import layering. It also routes HTML output through the renderer's safety helpers implicitly.

## File and symbol plan

- `src/mistune/__main__.py` · `_output` (edit) — Modify the `_output` function to check if `args.output` is '-' or '-o'. If so, use `sys.stdout` instead of opening a file.

## Test approach

Add unit tests in `tests/test_cli.py` to verify that `--output -` and `-o -` send the output to stdout, and that other filenames and existing files are handled correctly.
