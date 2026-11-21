# Component view

```mermaid
flowchart LR
    M[Maintainer] -->|label or exact command| G[Trigger gate]
    G -->|issue snapshot and base SHA| B[Build job]
    B --> R[Requirements agent]
    B --> D[Design agent]
    B --> W[Implementer and tester]
    R --> Q[Loopback Qwen inference]
    D --> Q
    W --> Q
    W -->|candidate tree| S[Offline build and pytest container]
    B -->|checked patch| P[Release job]
    P -->|branch and PR| GH[GitHub API]
    P -->|candidate SHA| CI[Independent CI workflow]
    CI -->|same SHA passed| P
    P -->|issue snapshot, PR number and SHA| V[Read-only review job]
    V -->|issue, final diff and repository| A[Reviewer agent]
    A --> Q2[Separate loopback Qwen process]
    V -->|verdict and findings| C[Review publisher]
    C -->|review on the PR| GH
    C -->|first round asks for changes| B
    GH -->|final decision| M
```

The workflow controls retries and permissions. Agents return structured data. The implementer proposes file contents, and the runner applies them under an allowlist. Release and review publication use separate jobs with the GitHub permissions for their specific operation.
