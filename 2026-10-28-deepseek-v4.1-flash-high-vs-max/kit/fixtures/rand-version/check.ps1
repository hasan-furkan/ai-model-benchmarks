# Gate: format, strict clippy, tests.
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
cargo fmt --check; if ($LASTEXITCODE) { 'CHECK FAILED: fmt'; exit 1 }
cargo clippy --all-targets -- -D warnings -D clippy::unwrap_used -D clippy::expect_used -D clippy::panic; if ($LASTEXITCODE) { 'CHECK FAILED: clippy'; exit 1 }
cargo test; if ($LASTEXITCODE) { 'CHECK FAILED: test'; exit 1 }
'CHECK PASSED'
