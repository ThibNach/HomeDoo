# start.ps1
$BackendJob = Start-Job -ScriptBlock {
    Set-Location "C:\_Work\Apps\HomeDoo\core\backend"
    poetry run python app.py
}

$FrontendJob = Start-Job -ScriptBlock {
    Set-Location "C:\_Work\Apps\HomeDoo\core\frontend"
    python -m http.server 3000 --bind 127.0.0.1
}

Write-Host "Backend running on http://127.0.0.1:5000"
Write-Host "Frontend running on http://127.0.0.1:3000"
Write-Host "Press Ctrl+C to stop"

try {
    Wait-Job $BackendJob, $FrontendJob
} finally {
    Stop-Job $BackendJob, $FrontendJob
    Remove-Job $BackendJob, $FrontendJob
}