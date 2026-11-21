# Sequence view

The diagram shows the local F1 probe, which used authored model responses and the same checks as the workflow. F1 is the original stdout-dash issue #3 and the active demo input. [Run ledger](../../results/runs.md)

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

## Hosted F1 attempt

```mermaid
sequenceDiagram
    participant M as Maintainer
    participant G as GitHub Actions intake
    participant Q as Loopback Qwen process
    participant A as Run artifacts
    M->>G: Dispatch issue 3 from the evidence branch
    G->>G: Check write access and pin the issue and main SHA
    G->>Q: Apply the compact A1 requirements prompt
    Q-->>G: Return a ready spec with observable criteria
    G->>A: Save the specification
    G->>Q: Request a design using the A2 architecture
    Q--xG: The design call times out
    G->>A: Save the failed gate and stop
```

The hosted release and review jobs were skipped. The separate reviewer comparison completed for all five seeded PRs. [F1 Actions run](https://github.com/khush2520/mistune/actions/runs/44836017315) · [Seeded reviewer Actions run](https://github.com/khush2520/mistune/actions/runs/44787096358)
