> Translated from the original Turkish prompt that the agents actually received.

First read STANDARDS.md. Project: Live Meeting Assistant (Tauri 2 + Rust `core/`, `src-tauri/` + React/TS `ui/`). The folder you are in is the project root; work only in this folder.

## Task 2: Memory that grows without bound during a long lecture (security review item M3)

**Background:** The user says the computer gets hot during long lectures; memory growth is suspected. Read item **M3** in `docs/security-review-2026-10-22.md`. Summary: the `Worker` in `core/src/session.rs` keeps every final line in `lines: Vec<String>` for the whole lecture; `recent_text` concatenates the entire vector on every analysis and on every name trigger; if the notes folder cannot be written, the `pending` queue grows without bound.

**Desired behaviour:**
1. **Sliding window:** `Worker` no longer keeps the whole transcript in memory. Only the last words are kept for the prompts: at least as many as the larger of the `RECENT_WORDS` and `CLASSIFY_WORDS` constants, with a fixed and reasonable upper bound (e.g. 2,000 words). However many hours the lecture lasts, the window never exceeds this bound.
2. `recent_text` (and the analysis/classification paths that use it) no longer concatenates the whole history; its cost is bounded by the window size. The text that goes to the analysis must not differ from today's (the last `RECENT_WORDS` / `CLASSIFY_WORDS` words stay the same).
3. **Summary from the file:** the summary at Stop is now read from the transcript file rather than from the in-memory vector (`retry_summary` already does this; use the `transcript_text` helper). This way old lines that have fallen out of the window are still included in the summary.
4. **Lines that could not be written:** if at Stop there are still lines not written to disk (`pending`), they are appended to the end of the summary text as well; no line silently drops out of the summary (file + pending, order preserved).
5. **`pending` bound:** the queue holds at most a fixed number of lines (e.g. 500). When it is full, the oldest line is dropped and the user is told once, via `SessionEvent::Error`, with a message like "Notes folder is not writable; oldest unsaved lines were dropped" (not repeatedly on every line).
6. If the file cannot be read, the Stop summary fails with `SummaryFailed` in a form that matches the existing error shape; no panic.
7. All other behaviour stays the same (notifications, triggers, the `-2` suffixes, retry).

**Tests (follow the existing `core` test layout; the fake STT/VAD/LLM helpers already exist, use them):**
- After a large number of lines (e.g. 10,000), the window bound is not exceeded.
- `recent_text` / the analysis text returns the last words correctly (both above and below the bound).
- The Stop summary includes the oldest line that had fallen out of the window (proving it was read from the file).
- With an unwritable folder the `pending` bound is not exceeded; the warning arrives only once.
- Lines pending at Stop time are included in the summary text.
- Malicious/edge input: empty lines, a single very long line (e.g. 100,000 characters), whitespace only.

**Rules:**
- Do not add a new dependency. Do not modify `scripts/check.ps1`, `deny.toml`, `STANDARDS.md`.
- `unwrap`/`expect`/`panic` only inside `#[cfg(test)]`.
- Do not `git commit`; leave the changes in the working tree.
- You may add a single "Fixed:" note line under M3 in `docs/security-review-2026-10-22.md`.

**Definition of done:** `powershell -NoProfile -File scripts/check.ps1` → last line `CHECK PASSED`. If it fails, fix it and run it again.

**Short report at the end:** changed functions, the bound values you chose and the reasoning, number of tests added, the last 3 lines of `check.log`.
