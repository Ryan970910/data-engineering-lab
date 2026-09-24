param(
    [Parameter(Mandatory=$true)][string]$LegacyRoot,
    [Parameter(Mandatory=$true)][string]$LegacyPython
)
$ErrorActionPreference = 'Stop'
$taskRepo = Split-Path -Parent $PSScriptRoot
$taskRuntime = Join-Path $taskRepo '.learning-runtime'
$taskPython = Join-Path $taskRuntime 'spark39-venv\Scripts\python.exe'
$taskJava = Join-Path $taskRuntime 'java17\jdk-17.0.20.1+1-jre'
foreach ($taskPath in @($taskPython, "$taskJava\bin\java.exe", $LegacyRoot, $LegacyPython)) {
    if (-not (Test-Path -LiteralPath $taskPath)) { throw "Required path absent: $taskPath" }
}
$env:JAVA_HOME = $taskJava
$env:TEMP = Join-Path $taskRuntime 'tmp'
$env:TMP = $env:TEMP
$env:PYSPARK_PYTHON = $taskPython
$env:PYSPARK_DRIVER_PYTHON = $taskPython
$env:SPARK_LOCAL_IP = '127.0.0.1'
$env:SPARK_LOCAL_DIRS = Join-Path $taskRuntime 'spark-local39'
$env:SPARK_PYTHON_UNPACKED = Join-Path $taskRuntime 'spark39-venv\Lib\site-packages'
$env:PYTHONPATH = "$PSScriptRoot\spark_windows;$taskRepo\src"
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:LEGACY_PROJECT_ROOT = $LegacyRoot
$env:LEGACY_PYTHON = $LegacyPython
New-Item -ItemType Directory -Force $env:TEMP | Out-Null
$taskRun = Join-Path $taskRuntime ('migration-check-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $taskRun | Out-Null
Push-Location $taskRepo
try {
    $taskCode = @'
import json, sys, unittest
from pathlib import Path
import pyspark
suite = unittest.defaultTestLoader.discover('tests/migration')
result = unittest.TextTestRunner(verbosity=2).run(suite)
evidence = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
            'skipped': len(result.skipped), 'python': sys.version, 'spark': pyspark.__version__,
            'airflow_executed': False, 'full_business_workflows_verified': False}
Path(sys.argv[1]).write_text(json.dumps(evidence, indent=2), encoding='utf-8')
raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
'@
    # Windows PowerShell 5 treats native stderr warnings as ErrorRecords.
    # Judge the process by its exit status and structured evidence instead.
    $ErrorActionPreference = 'Continue'
    & $taskPython -c $taskCode (Join-Path $taskRun 'evidence.json') *> (Join-Path $taskRun 'tests.txt')
    $taskExit = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    Get-Content (Join-Path $taskRun 'evidence.json')
    Write-Output "Raw log: $taskRun\tests.txt"
    if ($taskExit -ne 0) { throw "Migration checks failed or skipped: $taskExit" }
} finally { Pop-Location }
