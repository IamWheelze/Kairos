param(
  [string]$BindHost = "127.0.0.1",
  [int]$BindPort = 8000
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[+] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[x] $msg" -ForegroundColor Red }

$Root = Split-Path $PSScriptRoot -Parent
$Req  = Join-Path $Root "backend\requirements.txt"
if (-not (Test-Path $Req)) { Write-Err "Missing $Req"; exit 1 }

# Ensure Python 3.11 venv exists
$VenvDir = Join-Path $Root ".venv"
if (-not (Test-Path $VenvDir)) {
  Write-Info "Creating virtualenv (.venv) with Python 3.11"
  py -3.11 -m venv $VenvDir
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) { Write-Err "venv python not found at $VenvPython"; exit 1 }

Write-Info "Upgrading pip, setuptools, wheel"
& $VenvPython -m pip install --upgrade pip setuptools wheel

Write-Info "Installing dependencies"
& $VenvPython -m pip install -r $Req

# Ensure .env exists and configure ProPresenter
$EnvFile = Join-Path $Root "backend\.env"
if (-not (Test-Path $EnvFile)) {
  $Example = Join-Path $Root "backend\.env.example"
  if (Test-Path $Example) { Copy-Item $Example $EnvFile }
}

Write-Info "Configuring backend/.env for ProPresenter"
$ppHost = Read-Host "ProPresenter host (default 127.0.0.1)"
if ([string]::IsNullOrWhiteSpace($ppHost)) { $ppHost = "127.0.0.1" }
$ppPort = Read-Host "ProPresenter port (default 53535)"
if ([string]::IsNullOrWhiteSpace($ppPort)) { $ppPort = "53535" }
$ppPass = Read-Host "ProPresenter password (set in ProPresenter > Preferences > Network)"

# Write/update keys in .env
$envLines = @()
if (Test-Path $EnvFile) { $envLines = Get-Content $EnvFile }
function Upsert-Key($key, $val) {
  $pattern = "^$key="
  $idx = $envLines.FindIndex({ $_ -match $pattern })
  if ($idx -ge 0) { $envLines[$idx] = "$key=$val" } else { $envLines += "$key=$val" }
}
Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
public static class Ext { public static int FindIndex(this System.Collections.Generic.List<string> list, Func<string,bool> p){ for(int i=0;i<list.Count;i++){ if(p(list[i])) return i; } return -1; } }
"@ -ReferencedAssemblies 'System.Core' -ErrorAction SilentlyContinue | Out-Null

$envList = New-Object System.Collections.Generic.List[string]
foreach($l in $envLines){ $envList.Add($l) }
function Upsert($k,$v){
  $idx = [Ext]::FindIndex($envList, { param($x) $x -like "$k=*" })
  if ($idx -ge 0) { $envList[$idx] = "$k=$v" } else { $envList.Add("$k=$v") }
}
Upsert "PROP_HOST" $ppHost
Upsert "PROP_PORT" $ppPort
Upsert "PROP_PASSWORD" $ppPass
$envList | Set-Content -Encoding ASCII $EnvFile

Write-Warn "Ensure ProPresenter: Preferences > Network > Enable Network Control, set Port=$ppPort and Password to match."

Write-Info ("Starting Kairos at http://{0}:{1}" -f $BindHost, $BindPort)
& $VenvPython -m uvicorn backend.main:app --host $BindHost --port $BindPort --reload
