@echo off
setlocal enabledelayedexpansion

:: Get the current Python version
for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set "py_version=%%i"

:: Extract major, minor, and patch versions
for /f "tokens=1,2,3 delims=." %%a in ("%py_version%") do (
    set "major=%%a"
    set "minor=%%b"
    set "patch=%%c"
)

:: Check if the version is compatible with pynput
if "%major%"=="3" (
    if "%minor%"=="11" (
        echo Python version %py_version% is compatible with pynput.
    ) else (
        echo Python version %py_version% is not compatible with pynput.
        echo Opening download page for Python 3.11...
        start https://www.python.org/downloads/release/python-3110/
    )
) else (
    echo Python version %py_version% is not compatible with pynput.
    echo Opening download page for Python 3.11...
    start https://www.python.org/downloads/release/python-3110/
)

endlocal
pause
pip install -r req.txt
exit