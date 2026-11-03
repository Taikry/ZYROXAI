param (
    [string]$symbol = "XAUUSD",
    [string]$timeframe = "M5",
    [string]$action = "analyze",
    [string]$test = "true"
)

$url = $env:MAKE_WEBHOOK_URL
if (-not $url) {
    $envPath = if ($PSScriptRoot) { Join-Path $PSScriptRoot ".env" } else { ".env" }
    if (Test-Path $envPath) {
        Get-Content $envPath | ForEach-Object {
            $line = $_.Trim()
            if ($line -match '^MAKE_WEBHOOK_URL\s*=\s*(.+)$') {
                $url = $matches[1].Trim()
            }
            if (-not $env:TELEGRAM_CHAT_ID -and $line -match '^TELEGRAM_CHAT_ID\s*=\s*(.+)$') {
                $env:TELEGRAM_CHAT_ID = $matches[1].Trim()
            }
        }
    }
}
if (-not $url) {
    Write-Host "[ERROR] MAKE_WEBHOOK_URL environment variable or .env entry is required." -ForegroundColor Red
    exit 1
}

$payload = @{
    symbol    = $symbol
    timeframe = $timeframe
    action    = $action
    test      = ($test -in @("1", "true", "yes"))
}
if ($env:TELEGRAM_CHAT_ID) {
    $payload.chat_id = $env:TELEGRAM_CHAT_ID
}
$payloadJson = $payload | ConvertTo-Json

Write-Host "Sending webhook POST to configured Make webhook..." -ForegroundColor Cyan
Write-Host "URL: $url" -ForegroundColor Gray
Write-Host "Payload: $payloadJson" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri $url -Method Post -ContentType "application/json" -Body $payloadJson
    Write-Host "Response ($response)" -ForegroundColor Green
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
