# Hidden test score

| Candidate | Case | Passed | Total |
| --- | --- | ---: | ---: |
| Pinned baseline | B1 | 0 | 3 |
| Pinned baseline | B2 | 1 | 3 |
| Pinned baseline | F1 | 1 | 3 |
| Pinned baseline | F2 | 0 | 3 |
| Pinned baseline | F3 | 1 | 3 |
| Scripted local candidate | F1 | 3 | 3 |
| Scripted local intake | V1 | 2 | 2 |
| Temporary reference change | F3 | 3 | 3 |

Hidden tests were kept outside the repository. The baseline rows check that the suite can detect the reported gaps. The F1 and V1 candidates use authored model inputs.

The F3 reference ran in a temporary checkout to validate the new hidden tests. Issue #12 has no hosted agent result yet.
