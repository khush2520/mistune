# Requirements

Add a short `-V` flag for the CLI version

## Actors
- User

## Constraints
- The `-V` flag should print the same version line to stdout as `--version` and exit successfully.
- The `-V` flag should work without reading stdin.
- If `-m` is also passed, the version flag should still print only the version.
- A normal `-m` invocation should render Markdown as before.

## Assumptions
- The current version of Mistune can be accessed via `python -m mistune --version`.

## Questions

## Acceptance criteria

### AC-01 (FR-01, inferred)
- **Evidence** The `-V` flag should print the same version line to stdout as `--version` and exit successfully.
- **Given** A user runs `python -m mistune -V`.
- **When** The command is executed.
- **Then** The output should be the same version line as `python -m mistune --version` and the program should exit successfully.

### AC-02 (FR-02, inferred)
- **Evidence** The `-V` flag should work without reading stdin.
- **Given** A user runs `python -m mistune -V` with no input.
- **When** The command is executed.
- **Then** The program should not read from stdin and should exit successfully.

### AC-03 (FR-03, inferred)
- **Evidence** If `-m` is also passed, the version flag should still print only the version.
- **Given** A user runs `python -m mistune -m -V`.
- **When** The command is executed.
- **Then** The output should be the same version line as `python -m mistune --version` and the program should exit successfully.

### AC-04 (FR-04, inferred)
- **Evidence** A normal `-m` invocation should render Markdown as before.
- **Given** A user runs `python -m mistune -m` with Markdown input.
- **When** The command is executed.
- **Then** The output should be the rendered Markdown as before.

## A1 validation
- completeness — pass
- consistency — pass
- feasibility — pass
- testability — pass
- traceability — pass
