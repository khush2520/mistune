# Requirements

The issue requires clarification on the expected behavior for the `--output -` flag in the CLI tool.

## Actors
- User
- CLI Tool

## Constraints
- The CLI tool must support sending output to stdout using the `--output -` flag.
- The tool should use the normal stdout format for the `--output -` flag.
- Other filenames should still work with the tool.
- A file already called `-` should be left alone.

## Assumptions
- The user expects the `--output -` flag to work as a standard output redirection.
- The tool should handle filenames other than `-` as normal.
- The tool should not modify the behavior of a file already named `-`.

## Questions
- What is the expected behavior of the `--output -` flag in the CLI tool?
- How should the tool handle filenames other than `-`?
- What should the tool do if a file already named `-` is provided?

## Acceptance criteria

### AC-01 (FR-01, confirmed)
- **Evidence** The user's issue description.
- **Given** The user runs the CLI tool with the `--output -` flag.
- **When** The tool processes the command.
- **Then** The tool outputs the result to stdout in the normal format.

## A1 validation
- completeness — unresolved
- consistency — unresolved
- feasibility — unresolved
- testability — unresolved
- traceability — unresolved


## Stopped

Clarification or a testable specification is needed before design.
