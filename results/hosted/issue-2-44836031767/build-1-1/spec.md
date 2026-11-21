# Requirements

The `add_toc_hook` function should keep the `data-id` attribute value as the heading ID in the table of contents if no real `id` attribute with the same value exists.

## Actors
- User

## Constraints
- The `add_toc_hook` function should not modify the `data-id` attribute if a real `id` attribute with the same value exists.
- The `add_toc_hook` function should use the suffix if a real `id` attribute with the same value exists.

## Assumptions
- The `add_toc_hook` function is used to generate table of contents entries.
- The `data-id` attribute is used to identify the target element for the table of contents entry.

## Questions

## Acceptance criteria

### AC-01 (FR-01, inferred)
- **Evidence** The `add_toc_hook` function should keep the `data-id` attribute value as the heading ID in the table of contents if no real `id` attribute with the same value exists.
- **Given** A generated page with `<div data-id="toc_1"></div>` followed by its first heading.
- **When** The `add_toc_hook` function is executed.
- **Then** The heading should have the ID `toc_1`.

### AC-02 (FR-02, inferred)
- **Evidence** The `add_toc_hook` function should use the suffix if a real `id` attribute with the same value exists.
- **Given** A generated page with `<div id="toc_1"></div>` followed by its first heading.
- **When** The `add_toc_hook` function is executed.
- **Then** The heading should have the ID `toc_1_1`.

## A1 validation
- completeness — pass
- consistency — pass
- feasibility — pass
- testability — pass
- traceability — pass
