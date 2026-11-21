# Requirements

The issue requires clarification on the behavior of the `add_toc_hook` function and how it handles existing `id` attributes in HTML elements.

## Actors
- User

## Constraints
- The `add_toc_hook` function should not modify existing `id` attributes in HTML elements.
- The `add_toc_hook` function should use a suffix for the heading ID if a real `id` already exists.

## Assumptions
- The `add_toc_hook` function is responsible for generating table of contents entries.
- The `add_toc_hook` function is used with raw HTML enabled.
- The `add_toc_hook` function is reused across pages.

## Questions
- What is the expected behavior of the `add_toc_hook` function when it encounters an existing `id` attribute in an HTML element?
- How should the `add_toc_hook` function handle the case where a real `id` already exists, and what suffix should be used for the heading ID?

## Acceptance criteria

### AC-01 (FR-01, confirmed)
- **Evidence** The issue description
- **Given** A generated page with <div data-id="toc_1"></div> followed by its first heading.
- **When** The `add_toc_hook` function is executed.
- **Then** The heading should end up with `toc_1_1`, even though nothing on the page actually has `id="toc_1"`.

## A1 validation
- completeness — unresolved
- consistency — unresolved
- feasibility — unresolved
- testability — unresolved
- traceability — unresolved


## Stopped

Clarification or a testable specification is needed before design.
