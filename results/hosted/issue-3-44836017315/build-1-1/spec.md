# Requirements

Ensure CLI output is sent to stdout with --output -

## Actors
- User

## Constraints
- The `--output -` option should send the result to stdout.
- The `-o -` option should also send the result to stdout.
- Other filenames should still work.
- A file already called `-` should be left alone.

## Assumptions
- The current behavior writes a file called `-` instead of sending output to stdout.
- The CLI tool should handle filenames and special characters correctly.

## Questions

## Acceptance criteria

### AC-01 (FR-01, inferred)
- **Evidence** Our wrapper expects `--output -` to send the result down a pipeline.
- **Given** The user runs the CLI tool with the `--output -` option.
- **When** The tool processes the command.
- **Then** The output is sent to stdout.

### AC-02 (FR-02, inferred)
- **Evidence** The `-o -` option should also send the result to stdout.
- **Given** The user runs the CLI tool with the `-o -` option.
- **When** The tool processes the command.
- **Then** The output is sent to stdout.

### AC-03 (FR-03, inferred)
- **Evidence** Other filenames should still work.
- **Given** The user runs the CLI tool with a filename other than `-`.
- **When** The tool processes the command.
- **Then** The output is written to the specified file.

### AC-04 (FR-04, inferred)
- **Evidence** A file already called `-` should be left alone.
- **Given** The user runs the CLI tool with the `-` filename.
- **When** The tool processes the command.
- **Then** The output is written to the file named `-`.

## A1 validation
- completeness — pass
- consistency — pass
- feasibility — pass
- testability — pass
- traceability — pass
