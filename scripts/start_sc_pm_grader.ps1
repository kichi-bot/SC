$ErrorActionPreference = 'Stop'

$siteRoot = Split-Path -Parent $PSScriptRoot
$port = 8765
$url = "http://127.0.0.1:$port/html/sc_pm_grader.html"

function Test-GraderReady {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 2
        return $response.StatusCode -eq 200 -and $response.Content -match 'id="gradeButton"'
    }
    catch {
        return $false
    }
}

if (Test-GraderReady) {
    Start-Process $url
    exit 0
}

$listener = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
if ($listener) {
    $processIds = ($listener | Select-Object -ExpandProperty OwningProcess -Unique) -join ', '
    throw "Port $port is already used by another process. PID: $processIds"
}

$pythonw = Get-Command pythonw.exe -ErrorAction Stop
$serverScript = Join-Path $PSScriptRoot 'sc_pm_server.py'
& $pythonw.Source $serverScript

for ($attempt = 0; $attempt -lt 20; $attempt++) {
    Start-Sleep -Milliseconds 250
    if (Test-GraderReady) {
        Start-Process $url
        exit 0
    }
}

throw 'The grader server did not become ready in time.'
