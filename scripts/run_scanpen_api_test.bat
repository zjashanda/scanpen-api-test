@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
set "SCRIPT_DIR=%~dp0"

rem ===================== Editable parameters =====================
rem MODE: list-ports, validate, or stress. You can also pass it as the first argument.
set "MODE=validate"
set "CONFIG=%SCRIPT_DIR%..\assets\configs\default_scanInfo.json"
set "AP_PORT=COM6"
set "CP_PORT=COM3"
set "BAUD=921600"
set "LABEL=scanpen-api-test"
set "RESULT_BASE=%CD%\result"

rem Validate-mode parameters.
rem TEXT_B64 avoids .bat encoding problems. For validate, empty TEXT/TEXT_B64 uses base64 for Nihao.
rem For stress, empty TEXT/TEXT_B64 means using corpus text.
set "TEXT="
set "TEXT_B64="
set "LANGUAGE=0"
set "ROLE=1"
set "VOLUME=50"
set "SPEED=50"
set "TIMEOUT=20"

rem Stress-mode parameters.
set "COUNT=20"
set "OPS=trans,tts"
set "TEXT_BYTES=40"
set "RANDOM_TEXT_BYTES=0"
set "MIN_TEXT_BYTES=40"
set "MAX_TEXT_BYTES=120"
set "RANDOM_SEED="
set "CORPUS_KIND=random"
set "INTERVAL=1"
set "STOP_ON_FAIL=0"
set "FATAL_CONSECUTIVE_FAILURES=3"

rem Add extra raw arguments here, for example: --dry-run or --random-text-bytes.
set "EXTRA_ARGS="
rem ===============================================================

if not "%~1"=="" (
    set "MODE=%~1"
    shift
)

set "TAIL_ARGS="
:collect_args
if "%~1"=="" goto run
set "TAIL_ARGS=!TAIL_ARGS! %~1"
shift
goto collect_args

:run
set "SCRIPT=%SCRIPT_DIR%scanpen_api_runner.py"
set "STOP_ARG="
if "%STOP_ON_FAIL%"=="1" set "STOP_ARG=--stop-on-fail"
set "FATAL_ARG=--fatal-consecutive-failures %FATAL_CONSECUTIVE_FAILURES%"
set "RANDOM_ARG="
if "%RANDOM_TEXT_BYTES%"=="1" set "RANDOM_ARG=--random-text-bytes --min-text-bytes %MIN_TEXT_BYTES% --max-text-bytes %MAX_TEXT_BYTES%"
if not "%RANDOM_SEED%"=="" set "RANDOM_ARG=%RANDOM_ARG% --random-seed %RANDOM_SEED%"
if /I "%MODE%"=="validate" if "%TEXT%"=="" if "%TEXT_B64%"=="" set "TEXT_B64=5L2g5aW9"

python "%SCRIPT%" ^
  --mode "%MODE%" ^
  --config "%CONFIG%" ^
  --ap "%AP_PORT%" ^
  --cp "%CP_PORT%" ^
  --baud "%BAUD%" ^
  --label "%LABEL%" ^
  --result-base "%RESULT_BASE%" ^
  --text "%TEXT%" ^
  --text-b64 "%TEXT_B64%" ^
  --language "%LANGUAGE%" ^
  --role "%ROLE%" ^
  --volume "%VOLUME%" ^
  --speed "%SPEED%" ^
  --timeout "%TIMEOUT%" ^
  --count "%COUNT%" ^
  --ops "%OPS%" ^
  --text-bytes "%TEXT_BYTES%" ^
  --corpus-kind "%CORPUS_KIND%" ^
  --interval "%INTERVAL%" ^
  %STOP_ARG% %FATAL_ARG% %RANDOM_ARG% %EXTRA_ARGS% %TAIL_ARGS%

set "EXIT_CODE=%ERRORLEVEL%"
echo.
echo scanpen-api-test finished with exit code %EXIT_CODE%.
exit /b %EXIT_CODE%
