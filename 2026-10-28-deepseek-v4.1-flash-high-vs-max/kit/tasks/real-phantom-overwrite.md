> Translated from the original Turkish prompt that the agents actually received.

First read STANDARDS.md. Project: Live Meeting Assistant. The folder you are in is the project root; work only in this folder.

## Bug report (from the user)

Yesterday in the Algebra lecture I did Start/Stop twice on the same day (the first 40 minutes, the second 30 minutes). The summary of the second session overwrote the first session's `school/Algebra/2026-10-27-lesson.md` file; the first lecture's summary was lost completely. This is very bad, I lost my notes. Please fix this and write its test.

**Rules:** Do not add a new dependency. Do not modify `scripts/check.ps1`, `deny.toml`, `STANDARDS.md`. Do not `git commit`.

**Definition of done:** `powershell -NoProfile -File scripts/check.ps1` → last line `CHECK PASSED`.

**Short report at the end:** the root cause of the bug, what you changed, the tests added.
