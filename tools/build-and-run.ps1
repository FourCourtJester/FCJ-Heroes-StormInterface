<#
.SYNOPSIS
    Builds the FCJH .StormInterface and launches Heroes of the Storm on a replay.

.DESCRIPTION
    Replaces the builder's own --compileRun, which has no way to be told which game to
    launch and picks StarCraft II on this machine. We compile with --compile (reliable)
    and launch Heroes ourselves via HeroesSwitcher_x64.exe.

    Also works around two builder quirks:
      * The first run after a HotS patch dies re-parsing the base UI
        (IllegalStateException: Toolkit not initialized). It caches on the way down,
        so a second attempt succeeds.
      * The output .StormInterface is intermittently locked right after a write.
        We wait and retry rather than failing the whole loop.

.PARAMETER Replay
    Replay to launch. Defaults to the newest .StormReplay in the Heroes Accounts folder.

.PARAMETER NoRun
    Build only; do not launch the game.

.EXAMPLE
    .\tools\build-and-run.ps1
    .\tools\build-and-run.ps1 -NoRun
    .\tools\build-and-run.ps1 -Replay "C:\...\2026-08-09 20.27.30 Blackheart's Bay.StormReplay"
#>
[CmdletBinding()]
param(
    [string] $Replay,
    [switch] $NoRun
)

$ErrorActionPreference = 'Stop'

$RepoRoot   = Split-Path -Parent $PSScriptRoot
$Jar        = Join-Path $RepoRoot 'references\Galaxy-Observer-UI-HeroesFix\dev\compile-spring-boot.jar'
$Source     = Join-Path $RepoRoot 'builds\FCJH.StormInterface'
$Docs       = Join-Path $env:USERPROFILE 'OneDrive\Documents\Heroes of the Storm'
$Output     = Join-Path $Docs 'Interfaces\FCJH.StormInterface'
$Switcher   = 'C:\Program Files (x86)\Heroes of the Storm\Support64\HeroesSwitcher_x64.exe'

foreach ($p in @($Jar, $Source, $Switcher)) {
    if (-not (Test-Path -LiteralPath $p)) { throw "Not found: $p" }
}

if (Get-Process -Name 'Heroes of the Storm*' -ErrorAction SilentlyContinue) {
    throw 'Heroes is running and holds a lock on the interface file. Close it first.'
}

# --- XML well-formedness gate ----------------------------------------------------------
# The builder's "Validating Layouts" only resolves frame PATHS. It will happily build a
# file with unbalanced tags, producing an interface the game silently refuses to load -
# symptom is the stock UI with no build stamp. Catch it here instead.
Write-Host 'Checking layout XML...' -ForegroundColor Cyan
$bad = $false
Get-ChildItem (Join-Path $Source 'Base.StormData\UI\Layout') -Filter *.StormLayout -File | ForEach-Object {
    $raw   = [System.IO.File]::ReadAllText($_.FullName)
    $open  = ([regex]::Matches($raw, '<Frame\b(?![^>]*/>)')).Count
    $close = ([regex]::Matches($raw, '</Frame>')).Count
    try {
        $null = [xml]$raw
        if ($open -ne $close) { throw "tag count mismatch: $open open vs $close close" }
        Write-Host ("  OK   {0}  ({1} frames)" -f $_.Name, $open) -ForegroundColor DarkGray
    } catch {
        Write-Host ("  FAIL {0}: {1}" -f $_.Name, $_.Exception.Message) -ForegroundColor Red
        Write-Host ("       <Frame> {0} vs </Frame> {1}" -f $open, $close) -ForegroundColor Red
        $bad = $true
    }
}
if ($bad) { throw 'Layout XML is malformed. Fix before building - the builder will not catch this.' }

# --- Build, with retries for the two known transient failures --------------------------
$outFile = [System.IO.Path]::GetTempFileName()
$errFile = [System.IO.Path]::GetTempFileName()

$built = $false
foreach ($attempt in 1..3) {
    Write-Host "Building (attempt $attempt)..." -ForegroundColor Cyan

    # Start-Process rather than a direct call: in Windows PowerShell 5.1, redirecting a
    # native exe's stderr turns each line into a NativeCommandError, which combines with
    # ErrorActionPreference='Stop' to kill the script even on a clean exit code.
    Start-Process -FilePath 'java' `
                  -ArgumentList @('-jar', "`"$Jar`"", "`"--compile=$Source`"", '--noGUI') `
                  -NoNewWindow -Wait `
                  -RedirectStandardOutput $outFile -RedirectStandardError $errFile | Out-Null

    $log = (Get-Content -LiteralPath $outFile -Raw) + (Get-Content -LiteralPath $errFile -Raw)

    if ($log -match 'Finished building') { $built = $true; break }

    if ($log -match 'Toolkit not initialized') {
        Write-Host '  base UI was re-parsed (post-patch); retrying against the cache' -ForegroundColor Yellow
        continue
    }
    if ($log -match 'used by another process') {
        Write-Host '  output file locked; waiting 3s' -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        continue
    }

    # Anything else is a real error - surface the layout diagnostics and stop.
    ($log -split "`n" | Select-String -Pattern 'ERROR|WARNING: ') | ForEach-Object { Write-Host $_ -ForegroundColor Red }
    throw 'Build failed for a reason that is not a known transient. See above.'
}
if (-not $built) { throw 'Build did not succeed after 3 attempts.' }

$info = Get-Item -LiteralPath $Output
Write-Host ("Built {0:N0} bytes at {1:HH:mm:ss}" -f $info.Length, $info.LastWriteTime) -ForegroundColor Green

if ($NoRun) { return }

# --- Pick a replay and launch ----------------------------------------------------------
# Pinned default rather than newest-on-disk. Out-of-patch replays force a client version
# switch, and that switch WIPES the interface selection in Variables.txt - so a replay
# arriving from elsewhere silently hijacks the loop and shows the stock UI. Pin a known
# current-patch replay; override per-run with -Replay.
$PinnedReplay = Join-Path $Docs 'Accounts\118977\1-Hero-1-3468\Replays\Multiplayer\2026-08-09 20.27.30 Blackheart''s Bay.StormReplay'

if (-not $Replay) {
    if (Test-Path -LiteralPath $PinnedReplay) {
        $Replay = $PinnedReplay
    } else {
        Write-Host 'Pinned replay missing; falling back to newest on disk.' -ForegroundColor Yellow
        $newest = Get-ChildItem (Join-Path $Docs 'Accounts') -Recurse -Filter *.StormReplay -ErrorAction SilentlyContinue |
                  Sort-Object LastWriteTime -Descending |
                  Select-Object -First 1
        if (-not $newest) { throw 'No .StormReplay found. Pass -Replay explicitly.' }
        $Replay = $newest.FullName
    }
}
if (-not (Test-Path -LiteralPath $Replay)) { throw "Replay not found: $Replay" }

Write-Host "Launching: $(Split-Path -Leaf $Replay)" -ForegroundColor Cyan
& $Switcher $Replay
