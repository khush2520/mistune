# Design

Modify the `add_toc_hook` function in `src/mistune/toc.py` to check for the existence of a real `id` attribute before using the `data-id` attribute value for the heading ID in the table of contents. If a real `id` attribute exists, use the suffix to generate a unique ID.

## Architecture fit

The `add_toc_hook` function is part of the `toc.py` module, which is responsible for generating table of contents entries. The function should not modify the `data-id` attribute if a real `id` attribute with the same value exists, and should use the suffix if a real `id` attribute exists. This change will be made in the `add_toc_hook` function.

## File and symbol plan

- `src/mistune/toc.py` · `add_toc_hook` (edit) — Modify the `add_toc_hook` function to check for the existence of a real `id` attribute before using the `data-id` attribute value for the heading ID in the table of contents. If a real `id` attribute exists, use the suffix to generate a unique ID.

## Test approach

Write unit tests to verify that the `add_toc_hook` function correctly handles the `data-id` and `id` attributes. The tests should cover the following scenarios:
1. A generated page with `<div data-id="toc_1"></div>` followed by its first heading. The heading should have the ID `toc_1`.
2. A generated page with `<div id="toc_1"></div>` followed by its first heading. The heading should have the ID `toc_1_1`.
