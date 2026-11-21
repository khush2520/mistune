# Design

Modify the `_output` function in `src/mistune/__main__.py` to handle the `--output -` option by sending the result to stdout instead of writing to a file.

## Architecture fit

This change adheres to the constraints by not altering the token contract, extending through the `plugin(md)` mechanism, and respecting the import layering. It also routes HTML output through the renderer's safety helpers by using the existing `HTMLRenderer` methods.

## File and symbol plan

- `src/mistune/__main__.py` · `_output` (edit) — if args.output == '-':
    import sys
    sys.stdout.write(rendered_text)
else:
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(rendered_text)

## Test approach

Add a new test case in `tests/test_cli.py` to verify that the `--output -` option sends the result to stdout.
