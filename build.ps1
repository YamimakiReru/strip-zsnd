Set-Variable -Name APP_NAME -Value strip-zsnd -Option Constant

Set-Location $PSScriptRoot

Remove-Item .\build -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .\dist -Recurse -Force -ErrorAction SilentlyContinue

.\.venv\Scripts\Activate.ps1
& {
    $env:PYTHONPATH = "$PSScriptRoot\src"
    pyinstaller "$APP_NAME.spec"
}

Copy-Item -Path '.\locales' -Destination '.\dist\locales' -Recurse
