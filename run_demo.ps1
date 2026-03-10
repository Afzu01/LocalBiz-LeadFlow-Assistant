$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$port = 8101
$pythonExe = ".\.venv\Scripts\python.exe"

if (!(Test-Path $pythonExe)) {
	py -3.12 -m venv .venv
}

& $pythonExe -m pip install -r requirements.txt

# Start API server in a separate process so this script can open the browser.
Start-Process -FilePath $pythonExe -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--port", "$port" -WorkingDirectory $PSScriptRoot

Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:$port/ui"

Write-Host "LocalBiz LeadFlow Assistant is starting on http://127.0.0.1:$port"
Write-Host "Docs: http://127.0.0.1:$port/docs"
