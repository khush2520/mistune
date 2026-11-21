# Requirements

An explicitly empty message should work in the CLI

## Actors
- User

## Constraints
- The command should succeed when an empty string is passed as the message.
- The command should produce the same empty rendered result as an empty Markdown file.
- When passing an explicit message along with a file, the message should still win, even when the message is empty.

## Assumptions
- The current behavior is that passing an empty string as the message causes an error.
- The current behavior is that passing an explicit message along with a file results in the file being rendered with the message content.

## Questions

## Acceptance criteria

### AC-01 (FR-01, inferred)
- **Evidence** My script sometimes calls `python -m mistune --message ""` when a template has nothing in it.
- **Given** The user runs `python -m mistune --message ""`
- **When** the command is executed
- **Then** the command should succeed and produce an empty rendered result.

### AC-02 (FR-02, inferred)
- **Evidence** I want the command to succeed and produce the same empty rendered result as an empty Markdown file.
- **Given** The user runs `python -m mistune --message "" --output result.html`
- **When** the command is executed
- **Then** an empty file named `result.html` should be created.

### AC-03 (FR-03, inferred)
- **Evidence** If I pass an explicit message along with a file, the message should still win, even when the message is empty.
- **Given** The user runs `python -m mistune --message "" --output result.html --message "Hello, World!"`
- **When** the command is executed
- **Then** the file `result.html` should contain the content "Hello, World!".

## A1 validation
- completeness — pass
- consistency — pass
- feasibility — pass
- testability — pass
- traceability — pass
