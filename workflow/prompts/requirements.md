Apply the supplied A1 Requirements Engineer skill. This workflow packages the specification, assumptions/open questions, and validation summary together in spec.md. Do desk analysis only. Use the issue as the only stakeholder evidence. A project fact can be inferred and flagged. If a decision about behavior or which user problem to solve is still needed, return a blocked result and ask specific questions.

Return JSON with these fields:
- status (ready or blocked), summary (string), actors (array of strings), constraints (array of strings), assumptions (array of strings), questions (array of strings).
- criteria is an array. Each entry has id such as AC-01, requirement such as FR-01 or NFR-01, evidence (a brief reference to the issue), provenance (confirmed or inferred), given (test setup), when (an action), then (an observable expected result).
- checks is an object whose keys are completeness, consistency, traceability, feasibility, testability. Each value is the boolean outcome of your A1 validation.
For ready, provide one to eight criteria and no open questions. Keep the wording concrete. Keep compatibility constraints grounded in the issue.
