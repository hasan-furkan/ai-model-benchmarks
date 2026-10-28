> Translated from the original Turkish prompt that the agents actually received.

Compare and score two changes written by two different developers for the same task. Task: `task.md`. Changes: `A.diff` and `B.diff` (Live Meeting Assistant repository, Rust `core/`). Both passed the quality gate; do NOT modify the files, only read them.

For each of them:
1. Does it satisfy each of the 7 behaviour items in the task (yes / partly / no, with a diff line as evidence)?
2. Bugs: is the window really bounded (words or lines; does a single very long line break the bound), the cost of recent_text, reading the summary from the file and the order of pending lines, the pending bound and the warning being sent once, panic paths, concurrency. Every finding with a diff line.
3. Tests: which of the 6 test items in the task are actually tested; do they measure the behaviour?
4. Code quality.
5. A score of 1–10, one-sentence justification.

At the end a single table: | | A | B | and which one is better. Do not write a finding you have no evidence for.
