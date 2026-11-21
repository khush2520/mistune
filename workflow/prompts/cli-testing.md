For this CLI change, return cli_cases instead of test_code. Each case invokes python -m mistune in its own temporary directory and checks for exit code zero. Use the exact flags and file behavior requested in the original issue. If a flag has two requested aliases, exercise both in separate cases with the same criterion ID. Where the request says to leave an existing file alone, set its before and after fields to the same text.

JSON example for a CLI option that leaves normal stdout unchanged:
{"cli_cases":[{"id":"AC-01","args":["-m","## Example","--example-flag"],"same_stdout_as":["-m","## Example"]}]}

Each case has id and args. Use stdout for exact expected stdout or same_stdout_as for the argument list of an existing command whose nonempty stdout must match exactly. For a filesystem assertion, supply file with name (a basename), optional before (initial file contents), and after (expected exact file contents, or null if no file should exist). Test a real small Markdown input. Multiple cases may use the same criterion ID.
