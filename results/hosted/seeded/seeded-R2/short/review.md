# Independent review

**Verdict** approve

Commit `7a2a160fe5c3356fe642c095209898374fc9f1cf` · round 1.

The patch correctly handles the &#96;--output -&#96; option by printing to stdout when the output file is &#96;-&#96;. The tests pass, and there are no indications of breaking existing callers.

Independent checks run by the reviewer.
- build — exit 0
- test — exit 0
