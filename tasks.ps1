# AgentLab task runner (Windows / PowerShell)
#
# Usage:
#   .\tasks.ps1 setup
#   .\tasks.ps1 test
#   .\tasks.ps1 week 2
#   .\tasks.ps1 doctor
#   .\tasks.ps1 fmt
#   .\tasks.ps1 solution 1      # copies the reference solution for week 1 (last resort!)

param(
    [Parameter(Position = 0)]
    [ValidateSet('setup', 'sync', 'doctor', 'test', 'labs', 'week', 'fmt', 'lint', 'check', 'clean', 'solution', 'chat', 'help')]
    [string]$Task = 'help',

    [Parameter(Position = 1)]
    [string]$Week = '',

    [switch]$AllExtras,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Get-Uv {
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uv) {
        throw "uv is not installed. Install it with: powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`""
    }
    return $uv.Source
}

function Invoke-Uv {
    param([string[]]$Arguments)
    $uv = Get-Uv
    & $uv @Arguments
    if ($LASTEXITCODE -ne 0) { throw "uv $($Arguments -join ' ') failed with exit code $LASTEXITCODE" }
}

# For commands whose non-zero exit is meaningful (failing lab tests, an
# unconfigured doctor): run them, print the output, and propagate the code
# without a PowerShell exception trace.
function Invoke-UvAllowFailure {
    param([string[]]$Arguments)
    $uv = Get-Uv
    # Out-Host keeps the child output out of this function's return value, so
    # the caller receives only the exit code.
    & $uv @Arguments | Out-Host
    return $LASTEXITCODE
}

function Format-Week([string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value)) { throw "This command needs a week number, e.g. .\tasks.ps1 week 2" }
    return ('{0:D2}' -f [int]$Value)
}

switch ($Task) {
    'help' {
        Write-Host @"
AgentLab tasks

  .\tasks.ps1 setup          Create the Python 3.12 env, install dev deps, copy .env if missing
  .\tasks.ps1 sync           Re-sync dependencies (add -AllExtras for all optional extras)
  .\tasks.ps1 doctor         Check toolchain, keys and directories
  .\tasks.ps1 test           Run the whole test suite
  .\tasks.ps1 week 2         Run only that week's tests
  .\tasks.ps1 fmt            Format with ruff
  .\tasks.ps1 lint           Lint with ruff
  .\tasks.ps1 check          Lint + format check + full tests (what CI runs)
  .\tasks.ps1 chat           Start the terminal chat (week 1 deliverable)
  .\tasks.ps1 solution 1     Copy the reference solution for week 1 into place
  .\tasks.ps1 clean          Remove caches and local runtime artifacts

First time here? Read START-HERE.md, then run: .\tasks.ps1 setup
"@
        break
    }
    'setup' {
        Write-Host "[1/4] Installing Python 3.12 via uv..." -ForegroundColor Cyan
        Invoke-Uv @('python', 'install', '3.12')
        Write-Host "[2/4] Creating .venv and syncing dependencies..." -ForegroundColor Cyan
        Invoke-Uv @('sync', '--extra', 'dev')
        if (-not (Test-Path (Join-Path $Root '.env'))) {
            Copy-Item (Join-Path $Root '.env.example') (Join-Path $Root '.env')
            Write-Host "[3/4] Created .env from .env.example -- add your API keys." -ForegroundColor Yellow
        }
        else {
            Write-Host "[3/4] .env already exists, leaving it alone." -ForegroundColor DarkGray
        }
        Write-Host "[4/4] Running doctor..." -ForegroundColor Cyan
        $doctorCode = Invoke-UvAllowFailure @('run', 'python', '-m', 'agentlab.cli', 'doctor')
        if ($doctorCode -ne 0) {
            Write-Host "`nDoctor reported issues (expected until you add an API key)." -ForegroundColor Yellow
            Write-Host "Edit .env, then run: .\tasks.ps1 doctor" -ForegroundColor Yellow
        }
        Write-Host "`nSetup done. Next: read START-HERE.md" -ForegroundColor Green
        break
    }
    'sync' {
        $argsList = @('sync')
        if ($AllExtras) { $argsList += '--all-extras' } else { $argsList += @('--extra', 'dev') }
        Invoke-Uv $argsList
        break
    }
    'doctor' { exit (Invoke-UvAllowFailure @('run', 'python', '-m', 'agentlab.cli', 'doctor')) }
    'chat' { exit (Invoke-UvAllowFailure @('run', 'python', '-m', 'agentlab.cli', 'chat')) }
    'test' { exit (Invoke-UvAllowFailure @('run', 'pytest', '-q')) }
    'labs' { exit (Invoke-UvAllowFailure @('run', 'pytest', '-m', 'week', '-v')) }
    'week' {
        $w = Format-Week $Week
        exit (Invoke-UvAllowFailure @('run', 'pytest', "tests/week$w", '-m', 'week', '-v'))
    }
    'fmt' { Invoke-Uv @('run', 'ruff', 'format', '.') }
    'lint' { Invoke-Uv @('run', 'ruff', 'check', '--fix', '.') }
    'check' {
        Invoke-Uv @('run', 'ruff', 'check', '.')
        Invoke-Uv @('run', 'ruff', 'format', '--check', '.')
        Invoke-Uv @('run', 'pytest', '-q')
        break
    }
    'solution' {
        $w = Format-Week $Week
        $src = Join-Path $Root "solutions/week$w"
        if (-not (Test-Path $src)) { throw "No solution directory for week $w ($src)" }
        if (-not $Force) {
            $answer = Read-Host "This copies the week $w reference solution over your code. Type 'yes' to continue"
            if ($answer -ne 'yes') { Write-Host 'Cancelled.'; break }
        }
        Copy-Item -Recurse -Force (Join-Path $src '*') $Root
        Write-Host "Copied week $w solution over the repo. Re-run the tests to confirm." -ForegroundColor Yellow
        break
    }
    'clean' {
        $targets = @('.pytest_cache', '.ruff_cache', '.mypy_cache', 'htmlcov', '.coverage', 'data', 'traces')
        foreach ($t in $targets) {
            $p = Join-Path $Root $t
            if (Test-Path $p) { Remove-Item -Recurse -Force $p; Write-Host "removed $t" -ForegroundColor DarkGray }
        }
        Get-ChildItem -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force
        Write-Host 'Clean.' -ForegroundColor Green
        break
    }
}
