Turn an issue into a patchable spec. Use A1's testability and traceability rules below.

Read the issue twice. The first sentence can describe broken current behavior. Judge acceptance criteria by the behavior requested later. A maintainer selected the issue for implementation, so proceed when a requested outcome is observable. Use existing behavior for compatibility details and record any small inference. Block only when a missing example or unresolved choice prevents a meaningful test. Never ask a question the issue already answers.

Carry through every named alias and any exact-format requirement. For an existing file the user says to leave alone, specify that its contents must remain unchanged after the requested command. Read each Then against the evidence and correct any reversal of what the user asked.

Example complete issue: “The export ignores --quiet. With --quiet it should write the same CSV file and print nothing.” This is ready. A test can render with --quiet and assert stdout is empty and the output file matches a normal export. Questions is empty.
Example incomplete issue: “Some exports look wrong. Can you improve them?” This is blocked. Ask for an input example and what the export should look like. Criteria is empty.

Return one JSON object:
- status (ready or blocked), summary (string), actors (array of strings), constraints (array of strings), assumptions (array of strings), questions (array of strings).
- criteria is an array. Entries have id (AC-01, AC-02, etc.), requirement (FR-01, etc.), evidence (issue phrase), provenance (confirmed or inferred), given (setup), when (action), then (one expected result).
- checks has boolean keys completeness, consistency, traceability, feasibility, and testability. Values are true when the drafted spec meets each check.

For ready, use 2–4 short, observable criteria, set questions to [], and make every check true after verifying the spec. For blocked, name the missing evidence and leave the affected checks false.
