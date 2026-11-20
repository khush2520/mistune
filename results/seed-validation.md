# Seeded behavior checks

Each public fixture was applied to a disposable checkout and exercised through the CLI.

| Case | Observed behavior |
| --- | --- |
| R1 | preserved dash file |
| R2 | overwrote dash file |
| R3 | empty stdin incorrectly exited 0 |
| R4 | wrote selected file and preserved stdout path |
| R5 | wrote wrong output filename |
