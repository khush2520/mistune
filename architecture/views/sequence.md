# Sequence view

The diagram shows the local F1 probe. It uses authored model responses and the same checks as the workflow. The hosted issue, Actions run and review links belong in the [run ledger](../../results/runs.md).

```mermaid
sequenceDiagram
    participant I as F1 issue snapshot
    participant B as Builder
    participant C as Offline checker
    participant V as Independent review
    I->>B: Render output to stdout for a dash
    B->>B: Write spec and design
    B->>C: Build baseline code and run the new case
    C-->>B: Wheel passed, new test failed
    B->>C: Route the dash to stdout and retry
    C-->>B: Wheel and full suite passed
    B->>B: Validate patch and commit local candidate
    B->>V: Issue, committed diff and checkout
    V->>C: Request a fresh build and full suite
    C-->>V: Both passed
    V-->>I: Record fixture verdict in review.md
```

A hosted run inserts the release job between builder and review. The release job validates the patch again, pushes the branch, opens a PR, and waits for same-commit CI. A separate publisher posts the reviewer verdict on the PR.
