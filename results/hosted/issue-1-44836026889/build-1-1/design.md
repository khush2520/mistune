# Design

To address the issue, we need to modify the `cli` function in `src/mistune/__main__.py` to handle the case where an empty string is passed as the message. We will add a check to ensure that if the message is empty, the command proceeds without attempting to read from stdin. Instead, it will produce an empty rendered result as specified.

## Architecture fit

The change will be made in the `cli` function, which is part of the public API. This function is responsible for parsing command-line arguments and invoking the appropriate rendering method. By modifying this function, we can ensure that the command behaves as expected when an empty string is passed as the message.

## File and symbol plan

- `src/mistune/__main__.py` · `cli` (edit) — Add a check to ensure that if the message is empty, the command proceeds without attempting to read from stdin. Instead, it will produce an empty rendered result as specified.

## Test approach

We will add unit tests to verify that the command succeeds when an empty string is passed as the message and that it produces an empty rendered result. We will also add tests to ensure that the command behaves as expected when a non-empty message is passed along with a file.
