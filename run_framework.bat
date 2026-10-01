@echo off
setlocal

set "ROOT=%~dp0"
set "RUNNER=%ROOT%run_framework.py"

if defined VIRTUAL_ENV (
    set "PYTHON=%VIRTUAL_ENV%\Scripts\python.exe"
) else if defined CONDA_PREFIX (
    set "PYTHON=%CONDA_PREFIX%\python.exe"
) else (
    set "PYTHON=python"
)

if not exist "%PYTHON%" (
    set "PYTHON=python"
)

"%PYTHON%" "%RUNNER%" %*
exit /b %errorlevel%
