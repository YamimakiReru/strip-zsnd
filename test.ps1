Set-Location $PSScriptRoot
.\.venv\Scripts\Activate.ps1

$reportName = 'test-report'

pytest "--html=$reportName.html" --self-contained-html "--css=$reportName.css"
Start-Process "$reportName.html"
