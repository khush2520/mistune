# Independent review

**Verdict** approve

Commit `5ab011cfcb6e3f8f6b30a0b61c0419d440c5d242` · round 1.

The patch correctly handles the &#96;--output -&#96; option by writing to stdout instead of a file. The tests pass, and there are no indications of breaking existing callers.

Independent checks run by the reviewer.
- build — exit 0
- test — exit 0
