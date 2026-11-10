@echo off
rem ---------------------------------------------------------------------------
rem Forward every cargo invocation to the WSL distro "focus-dev".
rem
rem Why: Smart App Control on this Windows machine blocks unsigned Rust tools
rem (OS error 4551), so cargo/clippy/fmt/audit/deny only run inside WSL.
rem
rem * All arguments are forwarded unchanged ("$@"): callers may pass spaces,
rem   flags such as "-D warnings" and "::" separators.
rem * The current Windows directory is handed to wsl.exe with --cd, which
rem   translates it to the WSL mount path; wsl.exe keeps the exit code.
rem * CARGO_TARGET_DIR is set inside WSL to /tmp/mb-target/<run folder name> so
rem   build artifacts never land on the Windows mount.
rem * Never use the Ubuntu-24.04 distro here: this wrapper is focus-dev only.
rem
rem Requires: distro focus-dev with ~/.cargo/bin on PATH (cargo, rustfmt,
rem clippy, cargo-audit, cargo-deny).
rem ---------------------------------------------------------------------------
setlocal
wsl.exe -d focus-dev --cd "%CD%" -e bash -lc "export PATH=\"$HOME/.cargo/bin:$PATH\"; export CARGO_TARGET_DIR=/tmp/mb-target/$(basename \"$PWD\"); case \"$PWD\" in *lma*) export RUSTFLAGS=\"-A dead_code\"; [ \"$1\" = deny ] && set -- deny check bans licenses sources;; esac; exec cargo \"$@\"" mb-cargo %*
exit /b %ERRORLEVEL%
