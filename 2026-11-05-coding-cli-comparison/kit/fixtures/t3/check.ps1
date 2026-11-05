Set-Location $PSScriptRoot
py -3 -m unittest discover -s tests -t . -v; if ($LASTEXITCODE) { 'CHECK FAILED: test'; exit 1 }
'CHECK PASSED'
