Set-Location $PSScriptRoot
py -3 -m unittest -v; if ($LASTEXITCODE) { 'CHECK FAILED: test'; exit 1 }
'CHECK PASSED'
