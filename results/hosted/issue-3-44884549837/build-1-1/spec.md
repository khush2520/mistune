# Requirements

Ensure CLI output is sent to stdout with --output -

## Actors
- User

## Constraints
- The `--output -` option should send the result to stdout
- Other filenames should still work
- A file already called `-` should be left alone

## Assumptions
- The current behavior writes a file called `-` instead of sending to stdout
- The normal stdout format is consistent and expected

## Questions

## Acceptance criteria

### AC-01 (FR-01, inferred)
- **Evidence** Our wrapper expects `--output -` to send the result down a pipeline.
- **Given** The user runs the command with `--output -`
- **When** The command is executed
- **Then** The output is sent to stdout

### AC-02 (FR-02, inferred)
- **Evidence** Other filenames should still work
- **Given** The user runs the command with a filename other than `-`
- **When** The command is executed
- **Then** The output is written to the specified file

### AC-03 (FR-03, inferred)
- **Evidence** A file already called `-` should be left alone
- **Given** The user runs the command with a file already named `-`
- **When** The command is executed
- **Then** The output is written to the file `-`

## A1 validation
- completeness — pass
- consistency — pass
- feasibility — pass
- testability — pass
- traceability — pass
