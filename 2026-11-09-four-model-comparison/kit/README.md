# Four-model benchmark kit — 2026-11-09

This folder is the harness that ran the 2026-11-09 comparison of four OpenCode
Go arms. Reading it makes no model call; only `run_bench.py` without
`--dry-run` starts OpenCode.

**Public copy.** The original absolute benchmark root is replaced by the
placeholder `<bench-root>`. Paths below are relative to it. The task texts,
hidden tests and fixtures are not part of this public folder; `scoring.json`
names them by relative path. The published per-run data is in
`../results/runs.json`.

## Arms

| arm | exact `-m` value | effort |
|---|---|---|
| `luna` | `opencode-go/gpt-6-luna#medium` | medium |
| `deepseek` | `opencode-go/deepseek-v4.1-flash#high` | high |
| `mimo` | `opencode-go/mimo-v2.6-flash` | none (rejects `#high`) |
| `minimax` | `opencode-go/minimax-m3.1-flash#high` | high |

## Tasks

Round 1 used seven tasks; the extended round added thirteen. The task text is
handed to the model unchanged. Agent tasks edit a disposable copy and are
scored afterwards with hidden tests; no-tool tasks deny every permission and
are scored from the answer text. The no-tool prompts inside `bench_config.py`
are Turkish, the language they were written and run in; the scoring patterns
in `score.py` match Turkish and English answers. They are kept verbatim so the
public copy is the harness that actually ran.

| task | group | what it measures |
|---|---|---|
| `api` | agent-py | a new endpoint; hidden tests, gate and constraints |
| `stok` | agent-py | a race in a shared stock service; hidden tests, gate and constraints |
| `kod1` | no-tool | find the planted bug in a Python module |
| `kod2` | no-tool | find the planted bug in a second Python module |
| `belge1` | no-tool | check numbered statements against a document |
| `belge2` | no-tool | check numbered statements in a second document |
| `ghost` | no-tool | a bug report that is false; the right answer says the code is correct |
| `t1` | agent-cli | a new endpoint; gate, hidden tests and constraints |
| `t2` | agent-cli | a race on shared state; gate, hidden tests and constraints |
| `t3` | agent-cli | a behaviour-preserving refactor; gate, hidden tests and constraints |
| `t4` | agent-cli | a phantom bug in a small Python project; no production change |
| `t5` | agent-cli | a vague request with hidden rules; gate, hidden tests and constraints |
| `rc` | agent-rs | a Rust race; all hidden tests |
| `rand` | agent-rs | a pinned Rust version; all hidden tests |
| `zor1` | no-tool | an exact integer answer (460) |
| `zor2` | no-tool | an exact integer answer (1695) |
| `zor3` | no-tool | an exact integer answer (5019) |
| `lma1` | agent-lma | React/TS UI in a real Tauri project; gate |
| `lma2` | agent-lma | Rust backend in the same project; gate |
| `lmaghost` | agent-lma | a false bug report in the real project; gate and no production change |

Round 1: 7 tasks × 4 arms × 3 repeats = 84 runs. Extended round: 13 tasks ×
4 arms × 3 repeats planned = 156 runs, of which 94 completed; the round was
stopped early to save quota, so repeats per cell range from 1 to 3.

## Layout

```
kit/
  bench_config.py   paths, arms, tasks, prompts, hashing, isolation helpers
  events.py         OpenCode event parsing, session DB fallback, outside-path scan
  score.py          gate + hidden-test execution, auto_keyword checks
  run_bench.py      CLI runner (also has --dry-run)
  aggregate.py      runs.jsonl -> summary.md and summary.json
  scoring.json      configurable gate/hidden-test commands
  cli_constraints.py  constraint checks for the agent-cli fixtures
  shim/cargo.cmd    forwards cargo to the WSL distro
  shim/rust-gate.cmd  fmt, strict clippy and tests inside WSL
results/
  runs.json         filtered per-run metrics for the 178 completed runs
```

The original harness also had `testdata/` with hand-written rows for smoke-
testing `aggregate.py`. It is not part of this public copy.

## Commands

Run from `<bench-root>`:

```powershell
# Validate inputs and print the exact command forms; no model call.
python kit/run_bench.py --dry-run

# Pilot: all four arms, one repeat, stok + kod1 (8 model calls).
python kit/run_bench.py --pilot

# Round 1 matrix: 4 arms x 7 tasks x 3 repeats.
python kit/run_bench.py --tasks api,stok,kod1,kod2,belge1,belge2,ghost --reps 3 --parallel 3 --timeout 900

# Extended matrix: 4 arms x 13 tasks x 3 repeats (may stop early).
python kit/run_bench.py --tasks t1,t2,t3,t4,t5,rc,rand,zor1,zor2,zor3,lma1,lma2,lmaghost --reps 3 --parallel 3 --timeout 1800

# One arm, Rust tasks, two repeats.
python kit/run_bench.py --arms deepseek --tasks rs --reps 2

# Aggregate runs.jsonl into summary.md and summary.json.
python kit/aggregate.py
```

`--tasks` accepts task names (`api,stok,...`) or groups (`all`, `agent`, `py`,
`rs`, `cli`, `lma`, `notool`, `zor`). `--pilot` overrides tasks and reps.

## Isolation

* Each `run_id` (`<task>-<arm>-r<rep>`) gets a fresh folder under
  `%TEMP%\mb-2026-11-09\<run_id>\`, outside the benchmark tree. Fixture `.git`
  and `target` directories are not copied.
* The process starts with `cwd` and `PWD` set to that folder, because OpenCode
  takes the project directory from `PWD`.
* `OPENCODE_DISABLE_CLAUDE_CODE=1`; `CLAUDE*`, `ANTHROPIC*` and
  `DEEPSEEK_WORKER*` variables are dropped from the child environment.
* Agent tasks get `opencode.json` with `edit`/`bash` allowed,
  `external_directory` denied and web denied. No-tool tasks get
  `{"permission":{"*":"deny"}}`.
* Any absolute path named by a tool input that resolves outside the run folder
  is recorded in `outside_access_detail`; the run stays valid but is flagged.
  The report counts these flags but does not inspect their contents.
* After every run the session directory is compared with the run folder: first
  from `cwd`/`directory` fields in the event stream, then from OpenCode's
  session database. A mismatch or an unknown directory marks the run invalid
  (`session_dir_mismatch` / `session_dir_unknown`). `--no-session-check` turns
  this off and records `session_dir_verified: null`.
* Every persisted string is redacted against environment values whose names
  look like secrets; environment values themselves are never logged.

## Metrics and event parsing

`results/runs.jsonl` gets one JSON object per run, appended and `fsync`-ed
immediately. Fields include:

`run_id, task, group, arm, model, effort, rep, started_at, wall_seconds,
exit_code, timed_out, error_events, steps, tool_calls, input_tokens,
cache_read_tokens, cache_write_tokens, output_tokens, reasoning_tokens,
total_tokens, cost_usd, cost_source, hidden_pass, hidden_total, gate_passed,
files_changed, outside_access, valid, answer_chars`

plus `usage_source`, `missing_final_step_usage`, `session_id`,
`session_dir_verified`, `invalid_reasons`, `solved`, `auto_keyword` and
`artifacts` (per-run directory with the raw events, answer, gate log and hidden
test log). The published `runs.json` keeps only run identity, outcome, token,
cost and tool-call fields; local paths, prompts, answers and environment
details are removed.

Parsing details that matter:

* OpenCode mirrors each event in snake_case and kebab-case (and older harnesses
  mixed stderr into the same file), so events are de-duplicated by
  `type + part.id + timestamp`. Without this the token and cost sums double.
* A step may start and never emit `step-finish`; the process can still exit 1
  after a complete final answer. That is recorded as
  `missing_final_step_usage: true`. If the session database has usage for the
  session, those values are used instead and `usage_source` / `cost_source`
  become `session_db`; the partial step sums are kept under `step_usage`. No
  number is invented.
* `cost_usd` is whatever OpenCode reported (summed over `step-finish` events,
  or the session row), never a recomputed list price.

## Gate and hidden tests

`scoring.json` holds the commands. Hidden test files are copied in only for the
hidden run and removed afterwards.

* Python: `powershell -NoProfile -File check.ps1`, then
  `py -3 -m unittest -v <hidden module>`. Pass/total come from
  `Ran N tests` / `failures=` / `errors=`.
* Rust: commands run through `wsl.exe -e bash -lc`, because Smart App Control
  blocks unsigned cargo binaries on Windows. The Windows run folder is
  converted to its WSL mount path. Hidden `.rs` files are copied to
  `tests/<name>.rs` and run with `cargo test --test <name>`. Pass/total come
  from every `test result: ...` line (summed across test binaries). The gate
  command mirrors `check.ps1`: `cargo fmt --check`, strict clippy, then
  `cargo test`.
* The real-project (`lma*`) tasks use the project's own `scripts/check.ps1`.
  In the extended round two relaxations applied on Linux only: `dead_code` was
  allowed for Windows-only code, and `cargo deny` was limited to
  `bans licenses sources` because a crate had been yanked (not the security
  advisory set). The clean starting point passed the gate 9/9.
* Files generated by the gate (`ui/src/bindings`, `src-tauri/gen`) were not
  counted as production changes.

**Rust assumption:** WSL is installed, the project path is reachable from
WSL, and `cargo`, `rustfmt` and `clippy` are on the login shell's `PATH`. If
any of that is false, edit `kit/scoring.json`; the runner has no hard-coded
Rust invocation. Rust builds are the reason `--score-timeout` defaults to
900 s.

## No-tool scoring

Answers are saved in full. `auto_keyword` is a deliberately simple keyword
heuristic (function name + nearby fix hint; sentence numbers near
“wrong/yanlış”; “code is correct” for the ghost prompts). Every such row has
`score_source: "auto_keyword"` and `needs_human_review: true`, and
`aggregate.py` prints the same warning. These scores must not be presented as
model quality without a human reading of `answer.txt`. In the 2026-11-09
report the automatic score was unreliable and was not used; the quality table
comes from hand scoring against the answer key.

The `solved` field is the harness's own flag. On no-tool tasks it only means
the answer was non-empty, and on some timed-out rows it is true even though the
run failed. The report's pass counts come from the manual scoring and the
`timed_out` field, not from `solved`.

## Resuming

Run ids are stable. On restart, every `run_id` already present in
`results/runs.jsonl` is skipped; `--force` re-runs them. Run order is shuffled
with a fixed seed (`--seed`, default `20261109`) so arms are interleaved in
time. The input hash (kit + task texts + hidden tests + fixtures) is checked
before each run; if anything changes, the batch stops instead of mixing
generations.

## Verification status

The harness was written in a session where Python invocations were denied, so
the first version was reviewed statically for syntax and imports; it was not
compiled or executed at that point. It was then used for the benchmark: 178
rows in `results/runs.jsonl`, aggregated into `summary.json` and `summary.md`.
The pilot (`--pilot`) was the first real run. This public copy keeps the
scripts as used.
