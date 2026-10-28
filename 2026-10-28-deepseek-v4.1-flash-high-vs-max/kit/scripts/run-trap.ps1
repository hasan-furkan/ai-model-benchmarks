# One trap run: OpenCode worker in a fresh copy, then the manager's own gate + hidden test.
param([string]$Dir, [string]$Variant, [string]$TaskFile, [string]$Label, [string]$Hidden, [string]$HiddenDest, [string]$HiddenCmd)
$ErrorActionPreference = 'Continue'
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
$scratch = Split-Path -Parent $PSCommandPath
$out = Join-Path $scratch "trap-$Label.jsonl"
Set-Location $Dir
$sw = [Diagnostics.Stopwatch]::StartNew()
opencode run --standalone -m "opencode-go/deepseek-v4.1-flash#$Variant" --auto --format json --title "trap-$Label" --file $TaskFile "Carry out the attached task file completely. Follow its definition of done and finish with a short report." > $out 2>&1
$sec = [math]::Round($sw.Elapsed.TotalSeconds)
$sid = (Select-String -Path $out -Pattern '"sessionID":"(ses_[^"]+)"' | Select-Object -First 1).Matches.Groups[1].Value
$gate = (powershell -NoProfile -File check.ps1 2>&1 | Select-Object -Last 1)
$changed = (git status --short | ForEach-Object { $_.Trim() }) -join ', '
Copy-Item $Hidden (Join-Path $Dir $HiddenDest)
$hid = (cmd /c "$HiddenCmd 2>&1") -join "`n"
Remove-Item (Join-Path $Dir $HiddenDest)
"LABEL=$Label VARIANT=$Variant SECONDS=$sec SESSION=$sid GATE=$gate"
"CHANGED=$changed"
"HIDDEN:"
$hid
