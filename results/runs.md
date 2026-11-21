# Run ledger

Hosted model inference ran on free public GitHub Actions runners using Qwen2.5-Coder-7B-Instruct.
These links include stopped attempts. A vague issue stopping with actionable questions is an expected result.

| Case | Issue | Attempt | Actions | PR | CI | Posted review |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | [#1](https://github.com/khush2520/mistune/issues/1) | initial | [initial · failure](https://github.com/khush2520/mistune/actions/runs/44779316915) | — | — | — |
| B1 | [#1](https://github.com/khush2520/mistune/issues/1) | intake | [intake · failure](https://github.com/khush2520/mistune/actions/runs/44836026889) | — | — | — |
| B2 | [#2](https://github.com/khush2520/mistune/issues/2) | initial | [initial · failure](https://github.com/khush2520/mistune/actions/runs/44779323217) | — | — | — |
| B2 | [#2](https://github.com/khush2520/mistune/issues/2) | intake | [intake · failure](https://github.com/khush2520/mistune/actions/runs/44836031767) | — | — | — |
| F1 | [#3](https://github.com/khush2520/mistune/issues/3) | initial | [initial · failure](https://github.com/khush2520/mistune/actions/runs/44779300733) | — | — | — |
| F1 | [#3](https://github.com/khush2520/mistune/issues/3) | intake | [intake · failure](https://github.com/khush2520/mistune/actions/runs/44836017315) | — | — | — |
| F2 | [#4](https://github.com/khush2520/mistune/issues/4) | initial | [initial · failure](https://github.com/khush2520/mistune/actions/runs/44779329122) | — | — | — |
| F2 | [#4](https://github.com/khush2520/mistune/issues/4) | intake | [intake · failure](https://github.com/khush2520/mistune/actions/runs/44836037626) | — | — | — |
| V1 | [#5](https://github.com/khush2520/mistune/issues/5) | initial | [initial · failure](https://github.com/khush2520/mistune/actions/runs/44779310092) | — | — | — |
| V1 | [#5](https://github.com/khush2520/mistune/issues/5) | intake | [intake · failure](https://github.com/khush2520/mistune/actions/runs/44836022294) | — | — | — |

[Hosted issue results](results.csv) · [Local decision probes](local-probes.csv) · [Hidden baseline scores](hidden-scores.md)

## Seeded reviewer cases

[Hosted comparison run](https://github.com/khush2520/mistune/actions/runs/44787096358) · [Reviewer results](hosted/seeded.csv) · [CLI behavior checks](seed-validation.md)

| Case | Draft PR |
| --- | --- |
| R1 | [#6](https://github.com/khush2520/mistune/pull/6) |
| R2 | [#7](https://github.com/khush2520/mistune/pull/7) |
| R3 | [#8](https://github.com/khush2520/mistune/pull/8) |
| R4 | [#9](https://github.com/khush2520/mistune/pull/9) |
| R5 | [#10](https://github.com/khush2520/mistune/pull/10) |

## Dispatch block

After the two issue cohorts and the seeded reviewer comparison, GitHub rejected the compact revision's dispatch with HTTP 422, “Actions has been disabled for this repository.” The Actions permissions endpoint returned `enabled: true`, both workflows were `active`, and a later attempt returned the same error. GitHub did not create a run URL for either rejected request. The report keeps hosted PR and posted-review counts at zero.

B2 and F2 are scored against the candidate patches saved when testing stopped. Their patches were evaluated offline and were not released. V1 asked for an input example and the desired table, then stopped. The punctuation check in the hidden evaluator required a question mark, which the request did not have.
