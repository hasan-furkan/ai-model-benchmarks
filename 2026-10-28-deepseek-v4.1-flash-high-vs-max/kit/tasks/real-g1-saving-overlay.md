> Translated from the original Turkish prompt that the agents actually received.

First read STANDARDS.md. Project: Live Meeting Assistant (Tauri 2 + Rust `core/`, `src-tauri/` + React/TS `ui/`). The folder you are in is the project root; work only in this folder.

## Task 1: "Saving notes" indicator after Stop

**The user's request:** When Stop is pressed, a popup-like loading window should appear on screen while the summary (LLM) and the notes are being written, so the user can see that saving is still in progress.

**Current flow:** In `ui/src/views/Main.tsx`, `stop()` → `stopSession()` (`ui/src/api.ts`). When the summary finishes, the session event `SummaryWritten { path }` or `SummaryFailed { error }` arrives (the event listener in Main.tsx). The "Retry summary" button also waits for one of the same events through `retrySummary()`.

**Desired behaviour:**
1. The moment Stop is pressed, a modal overlay that dims the background opens at the top of the screen: a spinner, the text "Saving notes…" and the elapsed time in seconds ("12 s"). Accessibility: status text with `role="dialog"`, `aria-modal="true"`, `aria-live="polite"`.
2. The overlay closes when `SummaryWritten` or `SummaryFailed` arrives; the existing "Notes saved: …" / "Summary failed … Retry summary" areas keep working as before.
3. If `stopSession()` throws, the overlay closes immediately and the error is shown (the overlay must never get stuck).
4. If no event ever arrives, after 130 seconds the overlay closes and the warning "Saving is taking longer than expected; check the notes folder." is shown.
5. Pressing "Retry summary" opens the same overlay and it closes by the same rules.
6. While the overlay is open, the Start and Stop buttons cannot be clicked.
7. The visual style should match the existing dark theme in `ui/src/styles.css`; you may add new CSS classes.

**Tests (Vitest + Testing Library, follow the existing layout of `ui/src/views/Main.test.tsx`):**
- Pressing Stop makes the overlay visible; it closes on the `SummaryWritten` event and the path is shown.
- It closes on `SummaryFailed`, and the error and the Retry button are shown.
- If `stopSession` rejects, the overlay closes.
- With fake timers, the timeout warning appears after 130 s.
- The elapsed-time counter increases.
- Pressing Retry opens the overlay again.

**Rules:**
- Do not add a new dependency (npm/crate). Do not modify `scripts/check.ps1`, `deny.toml`, `STANDARDS.md`.
- Do not touch the Rust side unless necessary.
- Do not `git commit`; leave the changes in the working tree.

**Definition of done:** `powershell -NoProfile -File scripts/check.ps1` → last line `CHECK PASSED`. If it fails, fix it and run it again.

**Short report at the end:** changed files, number of tests added, the last 3 lines of `check.log`.
