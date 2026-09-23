$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$agentPath = Join-Path $repo "vesselframework_agent.py"

function Resolve-PythonCommand {
    if ($env:VIRTUAL_ENV) {
        $candidate = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        if (Test-Path $candidate) { return $candidate }
    }

    if ($env:CONDA_PREFIX) {
        $candidate = Join-Path $env:CONDA_PREFIX "python.exe"
        if (Test-Path $candidate) { return $candidate }
    }

    return "python"
}

$pythonCmd = Resolve-PythonCommand
& $pythonCmd $agentPath @args
exit $LASTEXITCODE