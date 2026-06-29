[CmdletBinding()]
param(
    [string]$Runner = "",
    [string]$Config = "",
    [string]$ResultBase = "",
    [int]$Count = 1000000,
    [string]$Ops = "trans,tts",
    [int]$TextBytes = 40,
    [int]$RandomTextBytes = 0,
    [int]$MinTextBytes = 40,
    [int]$MaxTextBytes = 120,
    [string]$CorpusKind = "random",
    [double]$Interval = 1,
    [int]$Language = 0,
    [int]$Role = 1,
    [int]$Volume = 50,
    [int]$Speed = 50,
    [double]$TimeoutSec = 30,
    [int]$StopOnFail = 1,
    [int]$FatalConsecutiveFailures = 3,
    [int]$WatchdogSec = 180,
    [string]$Text = "",
    [string]$TextB64 = "",
    [string]$ExtraArgs = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Runner)) {
    $Runner = Join-Path $PSScriptRoot "scanpen_api_runner.py"
}
if ([string]::IsNullOrWhiteSpace($Config)) {
    $Config = Join-Path $PSScriptRoot "..\assets\configs\default_scanInfo.json"
}
if ([string]::IsNullOrWhiteSpace($ResultBase)) {
    $ResultBase = Join-Path (Get-Location) "result"
}

$devices = @(
    [pscustomobject]@{ Name = "dev1"; Ap = "COM7";  Cp = "COM4"  },
    [pscustomobject]@{ Name = "dev2"; Ap = "COM8";  Cp = "COM6"  },
    [pscustomobject]@{ Name = "dev3"; Ap = "COM3";  Cp = "COM10" },
    [pscustomobject]@{ Name = "dev4"; Ap = "COM5";  Cp = "COM9"  },
    [pscustomobject]@{ Name = "dev5"; Ap = "COM20"; Cp = "COM24" },
    [pscustomobject]@{ Name = "dev6"; Ap = "COM22"; Cp = "COM23" },
    [pscustomobject]@{ Name = "dev7"; Ap = "COM25"; Cp = "COM18" },
    [pscustomobject]@{ Name = "dev8"; Ap = "COM19"; Cp = "COM21" }
)

function Normalize-CorpusKind {
    param([string]$Value)
    $v = ""
    if ($null -ne $Value) { $v = $Value.Trim().ToLowerInvariant() }
    switch -Regex ($v) {
        "^(chinese|china|cn|zh)$" { return "chinese" }
        "^(english|en)$" { return "english" }
        "^(mixed|mix)$" { return "mixed" }
        "^(random|rand|rnd)$" { return "random" }
        default { throw "Unsupported corpus kind '$Value'. Use chinese, english, mixed, or random." }
    }
}

function Split-ExtraArgs {
    param([string]$Line)
    if ([string]::IsNullOrWhiteSpace($Line)) { return @() }
    $matches = [regex]::Matches($Line, '"[^"]*"|\S+')
    $items = New-Object System.Collections.Generic.List[string]
    foreach ($m in $matches) {
        $value = $m.Value
        if ($value.Length -ge 2 -and $value.StartsWith('"') -and $value.EndsWith('"')) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        if ($value -ne "") { [void]$items.Add($value) }
    }
    return $items.ToArray()
}

function ConvertTo-ProcessArg {
    param([string]$Arg)
    if ($null -eq $Arg -or $Arg -eq "") { return '""' }
    if ($Arg -notmatch '[\s"]') { return $Arg }
    $escaped = $Arg.Replace('"', '\"')
    return '"' + $escaped + '"'
}

function Join-ProcessArgs {
    param([string[]]$ArgList)
    return (($ArgList | ForEach-Object { ConvertTo-ProcessArg $_ }) -join " ")
}
function Start-LoggedProcess {
    param(
        [string]$FilePath,
        [string]$Arguments,
        [string]$WorkingDirectory,
        [string]$StdoutPath,
        [string]$StderrPath
    )
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    $outWriter = New-Object System.IO.StreamWriter($StdoutPath, $false, $utf8NoBom)
    $errWriter = New-Object System.IO.StreamWriter($StderrPath, $false, $utf8NoBom)
    $outWriter.AutoFlush = $true
    $errWriter.AutoFlush = $true

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.Arguments = $Arguments
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    $proc.EnableRaisingEvents = $true
    $outEvent = Register-ObjectEvent -InputObject $proc -EventName OutputDataReceived -MessageData $outWriter -Action {
        if ($null -ne $EventArgs.Data) { $Event.MessageData.WriteLine($EventArgs.Data) }
    }
    $errEvent = Register-ObjectEvent -InputObject $proc -EventName ErrorDataReceived -MessageData $errWriter -Action {
        if ($null -ne $EventArgs.Data) { $Event.MessageData.WriteLine($EventArgs.Data) }
    }
    [void]$proc.Start()
    $proc.BeginOutputReadLine()
    $proc.BeginErrorReadLine()

    return [pscustomobject]@{
        Process = $proc
        OutWriter = $outWriter
        ErrWriter = $errWriter
        OutEvent = $outEvent
        ErrEvent = $errEvent
    }
}

function Close-LoggedProcess {
    param($Handle)
    if ($null -eq $Handle) { return }
    try {
        if ($null -ne $Handle.Process -and $Handle.Process.HasExited) { $Handle.Process.WaitForExit() }
    } catch {}
    foreach ($sub in @($Handle.OutEvent, $Handle.ErrEvent)) {
        if ($null -ne $sub) {
            try { Unregister-Event -SubscriptionId $sub.Id -ErrorAction SilentlyContinue } catch {}
            try { Remove-Job -Id $sub.Id -Force -ErrorAction SilentlyContinue } catch {}
        }
    }
    foreach ($writer in @($Handle.OutWriter, $Handle.ErrWriter)) {
        if ($null -ne $writer) {
            try { $writer.Flush() } catch {}
            try { $writer.Close() } catch {}
            try { $writer.Dispose() } catch {}
        }
    }
}

function Close-StateProcess {
    param($State)
    if ($null -eq $State -or $State.Closed) { return }
    Close-LoggedProcess $State.ProcessHandle
    $State.Closed = $true
}

function Get-DeviceResultDir {
    param([string]$Base, [string]$Label, [datetime]$StartedAfter)
    if (-not (Test-Path -LiteralPath $Base)) { return $null }
    $threshold = $StartedAfter.AddSeconds(-5)
    return Get-ChildItem -LiteralPath $Base -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "*-$Label" -and $_.CreationTime -ge $threshold } |
        Sort-Object CreationTime -Descending |
        Select-Object -First 1
}

function Get-LastActivityTime {
    param($State)
    $times = New-Object System.Collections.Generic.List[datetime]
    [void]$times.Add($State.StartTime)
    foreach ($path in @($State.StdoutLog, $State.StderrLog)) {
        if (Test-Path -LiteralPath $path) {
            [void]$times.Add((Get-Item -LiteralPath $path).LastWriteTime)
        }
    }
    if ($null -eq $State.ResultDir) {
        $State.ResultDir = Get-DeviceResultDir -Base $State.ResultBase -Label $State.Label -StartedAfter $State.StartTime
    }
    if ($null -ne $State.ResultDir -and (Test-Path -LiteralPath $State.ResultDir.FullName)) {
        $latest = Get-ChildItem -LiteralPath $State.ResultDir.FullName -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($null -ne $latest) { [void]$times.Add($latest.LastWriteTime) }
    }
    return ($times | Sort-Object -Descending | Select-Object -First 1)
}

$CorpusKind = Normalize-CorpusKind $CorpusKind
$ResultBase = [System.IO.Path]::GetFullPath($ResultBase)
New-Item -ItemType Directory -Force -Path $ResultBase | Out-Null

$runStamp = Get-Date -Format "yyyy-MM-dd_HH_mm_ss"
$supervisorDir = Join-Path $ResultBase ("multi8_supervisor_" + $runStamp)
New-Item -ItemType Directory -Force -Path $supervisorDir | Out-Null

$extra = Split-ExtraArgs $ExtraArgs
$states = New-Object System.Collections.Generic.List[object]

Write-Host "Starting 8 ScanPen stress workers..."
Write-Host "ResultBase=$ResultBase"
Write-Host "SupervisorDir=$supervisorDir"
Write-Host "Count=$Count Ops=$Ops Corpus=$CorpusKind TextBytes=$TextBytes RandomTextBytes=$RandomTextBytes Min=$MinTextBytes Max=$MaxTextBytes"
Write-Host "TimeoutSec=$TimeoutSec StopOnFail=$StopOnFail FatalConsecutiveFailures=$FatalConsecutiveFailures WatchdogSec=$WatchdogSec"
Write-Host ""

foreach ($d in $devices) {
    $label = "multi8-$($d.Name)-$($d.Ap)-$($d.Cp)"
    $stdout = Join-Path $supervisorDir ("$($d.Name)_$($d.Ap)_$($d.Cp).stdout.log")
    $stderr = Join-Path $supervisorDir ("$($d.Name)_$($d.Ap)_$($d.Cp).stderr.log")

    $argumentList = @(
        "-u", $Runner,
        "--mode", "stress",
        "--config", $Config,
        "--ap", $d.Ap,
        "--cp", $d.Cp,
        "--baud", "921600",
        "--count", [string]$Count,
        "--ops", $Ops,
        "--corpus-kind", $CorpusKind,
        "--text-bytes", [string]$TextBytes,
        "--min-text-bytes", [string]$MinTextBytes,
        "--max-text-bytes", [string]$MaxTextBytes,
        "--interval", [string]$Interval,
        "--label", $label,
        "--result-base", $ResultBase,
        "--text", $Text,
        "--text-b64", $TextB64,
        "--language", [string]$Language,
        "--role", [string]$Role,
        "--volume", [string]$Volume,
        "--speed", [string]$Speed,
        "--timeout", [string]$TimeoutSec,
        "--fatal-consecutive-failures", [string]$FatalConsecutiveFailures
    )
    if ($RandomTextBytes -eq 1) { $argumentList += "--random-text-bytes" }
    if ($StopOnFail -eq 1) { $argumentList += "--stop-on-fail" }
    if ($extra.Count -gt 0) { $argumentList += $extra }

    $argString = Join-ProcessArgs $argumentList
    $cmdLineFile = Join-Path $supervisorDir ("$($d.Name)_command.txt")
    ("python " + $argString) | Set-Content -LiteralPath $cmdLineFile -Encoding UTF8

    $handle = Start-LoggedProcess -FilePath "python" -Arguments $argString -WorkingDirectory $PSScriptRoot -StdoutPath $stdout -StderrPath $stderr
    $proc = $handle.Process
    $state = [pscustomobject]@{
        Name = $d.Name
        Ap = $d.Ap
        Cp = $d.Cp
        Label = $label
        Process = $proc
        ProcessHandle = $handle
        Closed = $false
        Pid = $proc.Id
        StartTime = Get-Date
        ResultBase = $ResultBase
        ResultDir = $null
        StdoutLog = $stdout
        StderrLog = $stderr
        Status = "Running"
        ExitCode = $null
        LastActivity = Get-Date
        WatchdogKilled = $false
    }
    [void]$states.Add($state)
    Write-Host ("Started {0}: AP={1} CP={2} PID={3}" -f $d.Name, $d.Ap, $d.Cp, $proc.Id)
}

Write-Host ""
try {
    while (@($states | Where-Object { $_.Status -eq "Running" }).Count -gt 0) {
        foreach ($s in ($states | Where-Object { $_.Status -eq "Running" })) {
            $p = $s.Process
            $p.Refresh()
            $s.LastActivity = Get-LastActivityTime $s
            if ($p.HasExited) {
                try { $p.WaitForExit() } catch {}
                $s.ExitCode = $p.ExitCode
                $s.Status = if ($s.ExitCode -eq 0) { "Passed" } else { "Failed" }
                Close-StateProcess $s
                Write-Host ("Finished {0}: PID={1} ExitCode={2} Status={3}" -f $s.Name, $s.Pid, $s.ExitCode, $s.Status)
                continue
            }
            if ($WatchdogSec -gt 0) {
                $idleSec = ((Get-Date) - $s.LastActivity).TotalSeconds
                if ($idleSec -ge $WatchdogSec) {
                    Write-Host ("Watchdog killing {0}: PID={1} idle={2:N0}s" -f $s.Name, $s.Pid, $idleSec)
                    try { $p.Kill() } catch {}
                    try { $p.WaitForExit() } catch {}
                    $s.WatchdogKilled = $true
                    $s.ExitCode = -9
                    $s.Status = "WatchdogKilled"
                    Close-StateProcess $s
                }
            }
        }
        Start-Sleep -Seconds 5
    }
}
finally {
    foreach ($s in ($states | Where-Object { $_.Status -eq "Running" })) {
        try {
            $s.Process.Refresh()
            if ($s.Process.HasExited) {
                try { $s.Process.WaitForExit() } catch {}
                $s.ExitCode = $s.Process.ExitCode
                $s.Status = if ($s.ExitCode -eq 0) { "Passed" } else { "Failed" }
            } else {
                $s.Process.Kill()
                try { $s.Process.WaitForExit() } catch {}
                $s.Status = "StoppedBySupervisor"
                $s.ExitCode = -10
            }
        } catch {
            $s.Status = "StoppedBySupervisor"
            $s.ExitCode = -10
        }
        Close-StateProcess $s
    }
}

$summary = foreach ($s in $states) {
    if ($null -eq $s.ResultDir) { $s.ResultDir = Get-DeviceResultDir -Base $s.ResultBase -Label $s.Label -StartedAfter $s.StartTime }
    [pscustomobject]@{
        device = $s.Name
        ap = $s.Ap
        cp = $s.Cp
        pid = $s.Pid
        status = $s.Status
        exit_code = $s.ExitCode
        watchdog_killed = $s.WatchdogKilled
        last_activity = $s.LastActivity
        result_dir = if ($null -ne $s.ResultDir) { $s.ResultDir.FullName } else { "" }
        stdout_log = $s.StdoutLog
        stderr_log = $s.StderrLog
    }
}

$summaryPath = Join-Path $supervisorDir "supervisor_summary.csv"
$summary | Export-Csv -LiteralPath $summaryPath -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "Supervisor summary: $summaryPath"
$summary | Format-Table -AutoSize

$failed = @($summary | Where-Object { $_.status -ne "Passed" })
if ($failed.Count -gt 0) { exit 2 }
exit 0



