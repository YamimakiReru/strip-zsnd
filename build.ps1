Set-Location $PSScriptRoot

Remove-Item .\build -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .\dist -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .\strip-zsnd.spec -ErrorAction SilentlyContinue

.\.venv\Scripts\Activate.ps1
pyinstaller --onefile --name strip-zsnd src/main.py

Remove-Item .\strip-zsnd.spec -ErrorAction SilentlyContinue
