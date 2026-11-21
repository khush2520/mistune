# AutoSE 3 · Issue to reviewed pull request

[khush2520/ase-a3](https://github.com/khush2520/ase-a3) is the submission repository. The issue trials and reviewer experiments ran on the actual [Mistune fork](https://github.com/khush2520/mistune), where the issue, CI and review links resolve. Launch the workflow on that fork.

The submission retains the pinned Mistune history at `f7ec702edfc1ad5579a76f881238841af266d93c`, the same baseline as A2. The first AutoSE commit, `02c859e`, records the architecture before the workflow code.

## Run an issue

Use [issue #3](https://github.com/khush2520/mistune/issues/3), the original request for `--output -` to use stdout, for the demo. The active issue list and all attempts are in the [run ledger](results/runs.md).

1. On the fork, open an issue with the behavior you want and an example.
2. As a repository maintainer, add the `autose` label or post exactly `/autose`.
3. Open the [Actions tab](https://github.com/khush2520/mistune/actions/workflows/autose.yml). Start with `spec.md`, then check `design.md`, `diff.patch` and `test_report.md`. If release succeeds, `pr.md` links to the PR and the CI run that checked its commit.
4. Read the independent review on the PR. Requests for changes can send the job back to design or implementation once. The final decision belongs to a maintainer.

The workflow now runs Qwen2.5-Coder-7B-Instruct locally on the standard Actions runner. The pinned Q4_K_M weights are public and the runner binds llama.cpp to loopback. No model API key or paid inference fallback is needed. Each model step writes the prompt and completion token counts to `usage.json`. [Model card](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF) · [Public Actions runner billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)

## Settings for a fresh fork

1. Enable Issues and Actions. Set the repository Actions variable `AUTOSE_FORK` to the full `owner/repository` name. Keep the repository public so the standard hosted runners are free.
2. In **Settings → Actions → General**, enable **Allow GitHub Actions to create and approve pull requests**. AutoSE records its verdict as a GitHub review comment on the exact commit. Require pull requests for `main` and enforce protection for administrators. [Actions permissions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
3. Create the `autose` label. Issue and comment triggers use the workflow on the default branch.
4. To test a workflow revision on the protected fork before it lands, dispatch **AutoSE CI** on the evidence branch with `base=issue` and `label` set to the issue number. This runs the same controller using the evidence branch's workflow and the current protected `main` as the product base.

## Read the evidence

- [Report](report.pdf)
- [Architecture](architecture/views/components.md), [sequence](architecture/views/sequence.md), [stage map](architecture/views/stage-map.md) and [decisions](architecture/decisions/)
- [Issue texts](experiment/issues/), [seeded cases](experiment/seeded_prs/) and [experiment variants](experiment/variants.md)
- [Run ledger](results/runs.md) and [hosted results](results/results.csv)
- [Demo video](demo.mp4) records the earlier F1 local verification and the hosted seeded-review run.

Repeat the local decision probes with Docker running.

```sh
docker build -t autose-checks:local workflow
python3 experiment/measure.py /tmp/autose-results
```

Use a fresh output directory. These probes use scripted model responses, which makes the checks repeatable. The independent reviewer in the hosted flow receives the issue, diff and files from the released commit. It can run the fixed build and full test suite in the same isolation as CI.

## Hosted run status

The hosted reviewer experiment finished on all five seeded PRs. Each concrete issue reached at least requirements in the later cohort, and the vague issue stopped to request an example. GitHub rejected the next dispatch with HTTP 422 even though repository Actions permissions show enabled and the workflows show active. GitHub later accepted the restored #3 demo runs. The latest retry built a wheel and stopped at testing when the generated test file did not parse. The ledger links the attempts and their saved artifacts. [Run ledger](results/runs.md) · [GitHub Actions settings guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)

## AI assistance

Codex helped draft the architecture records, implement the workflow, prepare the issue and regression fixtures, run the local checks, and assemble the report. The decision records are working drafts for the author to review and revise in their own words before submission. The original A1 skill and A2 architecture are reused directly.
