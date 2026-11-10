@echo off
rem Strict Rust gate for the agent-rs fixtures (rc, rand).
rem Every step is a cargo subcommand; each one goes through cargo.cmd (WSL).
rem No other tool is called here.
setlocal
call "%~dp0cargo.cmd" fmt --all --check
if errorlevel 1 exit /b 1
call "%~dp0cargo.cmd" clippy --all-targets -- -D warnings -D clippy::unwrap_used -D clippy::expect_used -D clippy::panic
if errorlevel 1 exit /b 1
call "%~dp0cargo.cmd" test
if errorlevel 1 exit /b 1
exit /b 0
