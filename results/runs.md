# Run ledger

## Hosted issue inputs

| Case | Issue | Actions run | PR | Review |
| --- | --- | --- | --- | --- |
| B1 | [#1](https://github.com/khush2520/mistune/issues/1) | Pending | — | — |
| B2 | [#2](https://github.com/khush2520/mistune/issues/2) | Pending | — | — |
| F1 | [#3](https://github.com/khush2520/mistune/issues/3) | Pending | — | — |
| F2 | [#4](https://github.com/khush2520/mistune/issues/4) | Pending | — | — |
| V1 | [#5](https://github.com/khush2520/mistune/issues/5) | Pending | — | — |

The hosted model key and provider spending limit must be ready before the five issue runs. The local checks use zero API tokens.

## Local evidence

The local probes use an offline Docker container and authored model responses. [Results CSV](results.csv) · [Raw local evidence](local/).

## Seeded reviewer cases

| Case | Draft PR |
| --- | --- |
| R1 | [#6](https://github.com/khush2520/mistune/pull/6) |
| R2 | [#7](https://github.com/khush2520/mistune/pull/7) |
| R3 | [#8](https://github.com/khush2520/mistune/pull/8) |
| R4 | [#9](https://github.com/khush2520/mistune/pull/9) |
| R5 | [#10](https://github.com/khush2520/mistune/pull/10) |

These draft PRs are evaluator fixtures. The local D8 measurements used the matching diffs and scripted reviewer responses. The [behavior checks](seed-validation.md) confirm the expected labels against the CLI.
