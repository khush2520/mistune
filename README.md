# AutoSE 3 · Issue to reviewed pull request

This assignment uses [khush2520/mistune](https://github.com/khush2520/mistune). Mistune is pinned to `f7ec702edfc1ad5579a76f881238841af266d93c`, the same baseline as A2. The first AutoSE commit, `02c859e`, records the architecture before the workflow code.

## Run an issue

1. On the fork, open an issue with the behavior you want and an example.
2. As a repository maintainer, add the `autose` label or post exactly `/autose`.
3. Open the [Actions tab](https://github.com/khush2520/mistune/actions/workflows/autose.yml). Start with `spec.md`, then check `design.md`, `diff.patch` and `test_report.md`. If release succeeds, `pr.md` links to the PR and the CI run that checked its commit.
4. Read the independent review on the PR. Requests for changes can send the job back to design or implementation once. The final decision belongs to a maintainer.

The default model for each role is `gpt-5.4-mini-2026-03-17`, with low reasoning effort. Each role starts a fresh request. Set `AUTOSE_MODEL` only if you need a different compatible snapshot. Each build and review artifact has `usage.json` with provider-reported token counts.

## Settings for a fresh fork

1. Enable Issues and Actions. Set the repository Actions variable `AUTOSE_FORK` to the full `owner/repository` name.
2. Set an enforced spending limit in the OpenAI project that will pay for the runs. Create a key for that project and save it as the repository Actions secret `OPENAI_API_KEY`. [OpenAI project limits](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform) · [GitHub Actions secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)
3. In **Settings → Actions → General**, enable **Allow GitHub Actions to create and approve pull requests**. AutoSE records its verdict as a GitHub review comment on the exact commit. Protect `main` by requiring pull requests and enforce protection for administrators. [Actions permissions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
4. Create the `autose` label. The workflow needs to be on the default branch for issue and comment triggers.

## Read the evidence

- [Report](report.pdf)
- [Architecture](architecture/views/components.md), [sequence](architecture/views/sequence.md), [stage map](architecture/views/stage-map.md) and [decisions](architecture/decisions/)
- [Issue texts](experiment/issues/), [seeded cases](experiment/seeded_prs/) and [experiment variants](experiment/variants.md)
- [Run ledger](results/runs.md) and [measured local results](results/results.csv)

Repeat the local decision probes with Docker running.

```sh
docker build -t autose-checks:local workflow
python3 experiment/measure.py /tmp/autose-results
```

Use a fresh output directory. These probes use scripted model responses, which makes the checks repeatable and avoids API charges. The independent reviewer in the hosted flow receives the issue, diff and files from the released commit. It can run the fixed build and full test suite in the same isolation as CI.

## AI assistance

Codex helped draft the architecture records, implement the workflow, prepare the issue and regression fixtures, run the local checks, and assemble the report. The decision records are working drafts for the author to review and revise in their own words before submission. The original A1 skill and A2 architecture are reused directly.
