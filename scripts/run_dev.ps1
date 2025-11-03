param(
  [string]$BindHost = "127.0.0.1",
  [int]$BindPort = 8000
)

if (Test-Path -Path "backend/.env") {
  Write-Host "Loading backend/.env"
  Get-Content backend/.env | ForEach-Object {
    if ($_ -match '^(?<k>[^#=]+)=(?<v>.*)$') {
      $k=$matches['k'].Trim(); $v=$matches['v']
      [System.Environment]::SetEnvironmentVariable($k,$v)
    }
  }
}

python -m uvicorn backend.main:app --host $BindHost --port $BindPort --reload
