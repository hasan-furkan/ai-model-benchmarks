# ai-model-benchmarks

[Türkçe](README.tr.md)

Benchmark reports on AI models, published as static pages on GitHub Pages.

Every report is designed, run and verified by **Claude Opus 5.5 (Claude Code)** — it writes the tasks, the hidden tests and the answer keys, starts every run, re-runs every quality gate itself and checks each worker claim before it is recorded. The repository belongs to **Hasan Furkan (HFK)**, who asks for the benchmarks and makes the final decision in each one.

There is no framework, no build step, no CDN and no analytics: plain HTML, CSS and ES2020 JavaScript, served as static files.

## How the repository is laid out

```
index.html              the list of reports (reads benchmarks.json)
benchmarks.json         one record per report
assets/report.css       shared styling for both pages (light and dark)
assets/report.js        shared language switch and page rendering
<report-id>/            one folder per report, id = YYYY-MM-DD-<slug>
  index.html            the report page (reads data.json)
  data.json             every number and sentence shown on the page
  kit/                  what the benchmark actually ran
```

## What is in a report folder

- `data.json` — the single source of truth for the page. The HTML contains no figures or sentences of its own: the page fetches `data.json` and builds the DOM with `textContent`. Numbers are formatted in the browser (thousands separators, `2 min 52 s` durations, dates), so the same file feeds both the Turkish and the English version.
- `kit/` — the benchmark material, kept so that anyone can see what was measured and repeat it:
  - `tasks/` — the task files handed to the agents;
  - `hidden-tests/` — the tests that decide whether a task was really solved;
  - `fixtures/` — the small projects (Rust, Python) used as trap tasks;
  - `answer-keys/` — the expected answers, including the planted-error key;
  - `planted-errors/` — the buggy code and documents used in the error-hunting rounds;
  - `scripts/` — the runners and helper scripts used during the runs.

`kit/` is preserved as it was used. It is not served as documentation and some of it is deliberately broken (that is the point of the trap tasks).

### The kit of the DeepSeek V4.1 Flash report

```
tasks/
  real-g1-saving-overlay.md          real task G1: "saving notes" overlay after Stop
  real-g2-memory-bound.md            real task G2: bounding Worker memory (security item M3)
  real-phantom-overwrite.md          bug report with no reproducible cause (the phantom)
  real-phantom-null.md               "sometimes returns null" report for correct code (rule vs. control)
  trap-rc-cycle.md                   trap: reference cycle leaks departments and employees
  trap-rand-version.md               trap: unpinned/old `rand` API against a fixed version
  trap-inventory-race.md             trap: stock reservation race under many threads
  trap-hidden-requirements-api.md    trap: requirements the prompt does not spell out
  blind-review-g1.md                 blind review of two ui/ diffs (A and B)
  blind-review-g2.md                 blind review of two core/ diffs (A and B)
hidden-tests/
  rc_cycle_hidden.rs                 leak checks for the `staffing` crate
  rand_version_hidden.rs             behaviour checks for the `dice` crate
  test_inventory_hidden.py           oversell / lost-update checks for the stock module
  test_api_hidden.py                 UTC, money-format and sorting checks for the orders API
fixtures/
  rc-cycle/                          Rust crate `staffing` (departments and employees)
  rand-version/                      Rust crate `dice` (rand helpers, `rand = 0.10.3` pinned)
  inventory-race/                    Python stock module
  inventory-correct/                 correct, locked stock module (phantom-null fixture)
  hidden-requirements-api/           Python JSON API
answer-keys/
  planted-errors-key.md              the planted bugs, traps and false statements, both rounds
  blind-review-g1-key.txt            which diff was high and which was max (ui/ round)
  blind-review-g2-key.txt            which diff was high and which was max (core/ round)
planted-errors/
  code_round1.py, code_round2.py     Python modules with planted bugs (and traps)
  facts_round1.md, facts_round2.md   numbered statements, some deliberately false
scripts/
  run-real-task.ps1                  one real-task run through the OpenCode worker
  run-trap.ps1                       one trap run plus the manager's own hidden test
  planted-errors-round1.py           round 1 prompts (code review and fact checking)
  planted-errors-round2.py           round 2 prompts (code review and fact checking)
  phantom-bug-api.py                 the "fix a bug that does not exist" probe
  hard-questions.py                  three hard counting questions per effort level
  hard-questions-ground-truth.py     brute-force answers for those three questions
  opencode-session-stats.py          cost, tokens and duration of a session from opencode.db
  opencode-tool-calls.py             tool calls (and errors) from a session log
  opencode-final-text.py             the last text parts of a session log
```

The task files under `tasks/` were translated from the original Turkish prompts the agents actually received; each file starts with that note. The log-parsing scripts expect the UTF-16 session logs the runner wrote.

## Adding a new report

1. Create a folder named `YYYY-MM-DD-<short-slug>` next to the existing report.
2. Add `data.json` in that folder, following the shape of an existing one. Every string shown on the page is either a plain string or an object with `tr` and `en` fields; text that has no English version (`people`, `setup`, `agents.*_detail`, `cost.note`, `traps[].hidden`) is shown unchanged in both languages.
3. Copy `index.html` from an existing report folder — it only loads `../assets/report.css`, `../assets/report.js` and the folder's own `data.json`, so nothing in it is report-specific.
4. Add one record to `benchmarks.json`:

   ```json
   {
     "id": "YYYY-MM-DD-<short-slug>",
     "date": "YYYY-MM-DD",
     "title": { "tr": "…", "en": "…" },
     "summary": { "tr": "…", "en": "…" },
     "path": "YYYY-MM-DD-<short-slug>/"
   }
   ```

   `summary` is the decision of that report, not a description of the benchmark. The index sorts records by `date`, newest first.
5. Run the pages from a web server, not from `file://` — `fetch()` is blocked on `file://` and the pages will show an explicit error instead:

   ```
   python -m http.server 8000
   ```

   then open <http://localhost:8000/>.

## Conventions

- Language: TR | EN switch in the top right. The default follows the browser language (Turkish if it starts with `tr`, English otherwise); the choice is stored in `localStorage` and `<html lang>` follows it.
- Theme: light and dark, following `prefers-color-scheme`.
- In the arm tables the **high** column carries a thin highlight: it is the effort level the project settled on.
- Contaminated results — a run that read another worker's work — are marked with a visible *contaminated / kirli* badge and are never silently treated as valid.
- Data is written to the DOM only through `textContent` and `createElement`. `innerHTML`, `eval` and `new Function` are not used anywhere.
- Every file and folder name in this repository, and all committed content, is in English — with two exceptions: the Turkish `README.tr.md` next to the English `README.md`, and the bilingual (`tr` / `en`) text inside each report's `data.json`.
