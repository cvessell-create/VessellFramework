@echo off
setlocal

set "ROOT=%~dp0"
set "AGENT=%ROOT%vesselframework_agent.py"

if defined VIRTUAL_ENV (
    set "PYTHON=%VIRTUAL_ENV%\Scripts\python.exe"
) else if defined CONDA_PREFIX (
    set "PYTHON=%CONDA_PREFIX%\python.exe"
) else (
    set "PYTHON=python"
)

"%PYTHON%" "%AGENT%" %*
exit /b %errorlevel%