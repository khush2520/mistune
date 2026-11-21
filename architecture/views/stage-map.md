# Stage map

| Stage | Responsible role | Artifact | Gate |
| --- | --- | --- | --- |
| 1. Requirements | Requirements agent using A1 | `spec.md` | Given/When/Then criteria, evidence and all five A1 checks. Open questions stop the run. |
| 2. Design | Designer using A2 | `design.md` | Named paths and symbols must match the AST index for edited code. New symbols are explicitly declared. |
| 3. Implementation | Implementer | `diff.patch` | Proposed source is restricted to declared files, preserves planned symbols, parses as Python and builds a wheel offline. For a single conditional, the runner can route model-selected values to its existing else branch. |
| 4. Testing | Tester | `test_report.md` | The tester proposes CLI arguments and expected behavior, which the runner compiles into pytest. The full suite passes and each acceptance criterion has a passing JUnit case. One failure can return to implementation. |
| 5. Release | Release script | `pr.md` and PR URL | GitHub PR is open and the dispatched CI run succeeds for the exact head SHA. |
| 6. Review | Independent reviewer and separate publisher | `review.md` and review URL | Approval ends the run. The first request for changes can route back to design or implementation. The second ends the run with the finding visible. |

Each stage produces an explanation in its artifact if its check stops the run. Setup and infrastructure failures appear in the relevant job log and its artifact when the runner is still available.
