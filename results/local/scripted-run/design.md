# Design

Reuse the existing stdout branch when the output flag is a dash.

## Architecture fit

Keep the CLI dispatcher in __main__.py. Leave parsers and renderers alone.

## File and symbol plan

- `src/mistune/__main__.py` · `_output` (edit) — Use stdout for a dash.

## Test approach

Use a CLI subprocess with a pre-existing dash file.
