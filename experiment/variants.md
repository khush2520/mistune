# Decision experiments

## D7 · What should count as acceptance coverage?

Keep the same test repository and one criterion. Evaluate each of five candidate tests twice. The definition-only variant stops when the expected test definition is missing. The executed-case variant also checks the full suite exit code and verifies that pytest reported a passing test for that criterion. The probes cover an ordinary pass, a skip, an assertion failure, a function absent from collection, and a missing definition.

## D8 · What can a review publisher trust?

Use the same five seeded diffs and the same scripted reviewer replies. The verdict-only variant accepts each verdict string as returned. The evidence gate requires approval to have zero blocking findings, a change request to include at least one finding, and each finding to cite a real line at the released commit. This probe measures the output validation boundary. It does not estimate a model’s ability to find regressions.

For the live follow-up, use the same snapshot and diff for both prompt variants, restart all five review contexts, and compare each decision against `seeded_prs/labels.csv`. Record false alarms and missed regressions separately from invalid output. Keep labels outside reviewer prompts.
