@echo off
REM This batch is the "open with" handler for .neel files

REM %1 is the full path of the .neel file being opened
SET NEEL_FILE=%~1

IF "%NEEL_FILE%"=="" (
    echo Error: No file provided.
    pause
    exit /b 1
)

REM === Paths to your tools ===
SET PYTHON_PATH=python
SET NODE_PATH=node
SET SERVER_JS=E:\Neels Programs\first lang\server.cjs
SET COMPILE_PY=E:\Neels Programs\first lang\compile.py

REM === Compile the .neel file dynamically ===
"%PYTHON_PATH%" "%COMPILE_PY%" "%NEEL_FILE%"

REM === Determine compiled folder dynamically ===
FOR %%F IN ("%NEEL_FILE%") DO SET COMPILED_FOLDER=%%~dpFcompiled

REM === Start Node server with compiled folder ===
start "" "%NODE_PATH%" "%SERVER_JS%" "%COMPILED_FOLDER%"

REM === Give Node a second to start, then open browser ===
timeout /t 2 /nobreak >nul
start "" "http://neel.fun/"
