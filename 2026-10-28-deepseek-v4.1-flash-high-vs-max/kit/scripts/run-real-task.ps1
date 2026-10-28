# One benchmark run: fresh branch from main, OpenCode worker with the given variant, then usage from opencode.db.
param([string]$Dir, [string]$Variant, [string]$TaskFile, [string]$Label)
$ErrorActionPreference = 'Continue'
# This machine has VS 2026 only; env.ps1 would default to the 2022 generator.
$env:CMAKE_GENERATOR = 'Visual Studio 18 2026'
$scratch = Split-Path -Parent $PSCommandPath
$out = Join-Path $scratch "real-$Label.jsonl"
Set-Location $Dir
git checkout -q main; git reset -q --hard; git clean -qfd -e ui/node_modules -e target
git checkout -q -B "bench/$Label"
$sw = [Diagnostics.Stopwatch]::StartNew()
opencode run --standalone -m "opencode-go/deepseek-v4.1-flash#$Variant" --auto --format json --title "real-$Label" --file $TaskFile "Carry out the attached task file completely. Follow its definition of done and finish with a short report." > $out 2>&1
$sec = [math]::Round($sw.Elapsed.TotalSeconds)
$sid = (Select-String -Path $out -Pattern '"sessionID":"(ses_[^"]+)"' | Select-Object -First 1).Matches.Groups[1].Value
# Gate rerun by the manager, not the worker's word.
powershell -NoProfile -File scripts/check.ps1 *> $null
$gate = $LASTEXITCODE
$tail = (Get-Content check.log -Tail 1)
git add -A; git -c user.name=bench -c user.email=bench@local commit -qm "bench $Label" --allow-empty
$diff = git diff --shortstat main HEAD
"LABEL=$Label VARIANT=$Variant SECONDS=$sec SESSION=$sid GATE_EXIT=$gate GATE_LAST=$tail DIFF=$diff"
