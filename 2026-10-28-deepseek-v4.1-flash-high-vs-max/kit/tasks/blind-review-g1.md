> Translated from the original Turkish prompt that the agents actually received.

Compare and score two changes written by two different developers for the same task. Task: `task.md`. Changes: `A.diff` and `B.diff` (for the Live Meeting Assistant repository, inside the React/TS `ui/`). Both passed the quality gate; do NOT modify the files, only read them.

For each of them:
1. Does it satisfy each of the 7 behaviour items in the task (yes / partly / no, with an evidence line)?
2. Bugs: timer/leak (are setInterval/setTimeout cleaned up?), race conditions (event arriving before Stop returns, a second Stop, during Retry), accessibility, paths where the overlay can get stuck. A diff line for every finding.
3. Tests: which of the 6 test items in the task are actually tested; do the tests measure the behaviour or merely repeat the implementation?
4. Code quality: readability, unnecessary complexity.
5. A score of 1–10 and a one-sentence justification.

At the end a single table: | | A | B | and which one is better, with a short justification. Do not speculate: do not write a finding you have no evidence for.
