@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem 8-device ScanPen stress entry. Argument style follows run_scanpen_stress.bat.
rem Device map:
rem   dev1 AP=COM7  CP=COM4
rem   dev2 AP=COM8  CP=COM6
rem   dev3 AP=COM3  CP=COM10
rem   dev4 AP=COM5  CP=COM9
rem   dev5 AP=COM20 CP=COM24
rem   dev6 AP=COM22 CP=COM23
rem   dev7 AP=COM25 CP=COM18
rem   dev8 AP=COM19 CP=COM21

set "SCRIPT_DIR=%~dp0"
set "RUNNER=%SCRIPT_DIR%scanpen_api_runner.py"
set "CONFIG=%SCRIPT_DIR%..\assets\configs\default_scanInfo.json"
set "SUPERVISOR=%SCRIPT_DIR%run_scanpen_8_stress.ps1"
set "RESULT_BASE=%CD%\result"

rem Defaults. Edit here if needed.
set "COUNT=1000000"
set "OPS=trans,tts"
set "TEXT_BYTES=40"
set "RANDOM_TEXT_MIN=40"
set "RANDOM_TEXT_MAX=120"
set "CORPUS_KIND=random"
set "INTERVAL=1"
set "LANGUAGE=0"
set "ROLE=1"
set "VOLUME=50"
set "SPEED=50"
set "TIMEOUT=30"
set "STOP_ON_FAIL=1"
set "FATAL_CONSECUTIVE_FAILURES=3"
set "WATCHDOG_SECONDS=180"
set "EXTRA_ARGS="

rem Leave TEXT/TEXT_B64 empty to use generated corpus text in stress mode.
set "TEXT="
set "TEXT_B64="

rem Usage:
rem   run_scanpen_8_stress.bat
rem   run_scanpen_8_stress.bat 20
rem   run_scanpen_8_stress.bat 20 40 chinese
rem   run_scanpen_8_stress.bat 20 120 english
rem   run_scanpen_8_stress.bat 20 120 mixed
rem   run_scanpen_8_stress.bat 20 120 random
rem   run_scanpen_8_stress.bat 20 random
rem   run_scanpen_8_stress.bat 20 random 40 120 random
rem Corpus kind: chinese, english, mixed, random. Aliases zh/cn/en/mix/rand are also accepted by the supervisor.
rem Extra runner args can be appended, for example: --dry-run or --random-seed 1234

if not "%~1"=="" (
  set "COUNT=%~1"
  shift
)
if not "%~1"=="" (
  set "TEXT_BYTES=%~1"
  shift
)

set "RANDOM_ENABLED=0"
if /I "%TEXT_BYTES%"=="random" set "RANDOM_ENABLED=1"
if /I "%TEXT_BYTES%"=="rand" set "RANDOM_ENABLED=1"

if "%RANDOM_ENABLED%"=="1" goto parse_random_args

goto parse_fixed_args

:parse_fixed_args
if not "%~1"=="" (
  set "CORPUS_KIND=%~1"
  shift
)
goto after_mode_args

:parse_random_args
if not "%~1"=="" (
  set "RANDOM_TEXT_MIN=%~1"
  shift
)
if not "%~1"=="" (
  set "RANDOM_TEXT_MAX=%~1"
  shift
)
if not "%~1"=="" (
  set "CORPUS_KIND=%~1"
  shift
)
set "TEXT_BYTES=%RANDOM_TEXT_MAX%"
goto after_mode_args

:after_mode_args
set "TAIL_ARGS="
:tail_loop
if "%~1"=="" goto run
set "TAIL_ARGS=!TAIL_ARGS! %~1"
shift
goto tail_loop

:run
if not exist "%SUPERVISOR%" (
  echo ERROR: supervisor script not found: %SUPERVISOR%
  exit /b 2
)

if "%RANDOM_ENABLED%"=="1" (
  echo COUNT=%COUNT% OPS=%OPS% TEXT_BYTES=random %RANDOM_TEXT_MIN%-%RANDOM_TEXT_MAX% CORPUS=%CORPUS_KIND%
) else (
  echo COUNT=%COUNT% OPS=%OPS% TEXT_BYTES=%TEXT_BYTES% CORPUS=%CORPUS_KIND%
)
echo RESULT_BASE=%RESULT_BASE%
echo TIMEOUT=%TIMEOUT% STOP_ON_FAIL=%STOP_ON_FAIL% FATAL_CONSECUTIVE_FAILURES=%FATAL_CONSECUTIVE_FAILURES% WATCHDOG_SECONDS=%WATCHDOG_SECONDS%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%SUPERVISOR%" ^
  -Runner "%RUNNER%" ^
  -Config "%CONFIG%" ^
  -ResultBase "%RESULT_BASE%" ^
  -Count "%COUNT%" ^
  -Ops "%OPS%" ^
  -TextBytes "%TEXT_BYTES%" ^
  -RandomTextBytes "%RANDOM_ENABLED%" ^
  -MinTextBytes "%RANDOM_TEXT_MIN%" ^
  -MaxTextBytes "%RANDOM_TEXT_MAX%" ^
  -CorpusKind "%CORPUS_KIND%" ^
  -Interval "%INTERVAL%" ^
  -Language "%LANGUAGE%" ^
  -Role "%ROLE%" ^
  -Volume "%VOLUME%" ^
  -Speed "%SPEED%" ^
  -TimeoutSec "%TIMEOUT%" ^
  -StopOnFail "%STOP_ON_FAIL%" ^
  -FatalConsecutiveFailures "%FATAL_CONSECUTIVE_FAILURES%" ^
  -WatchdogSec "%WATCHDOG_SECONDS%" ^
  -Text "%TEXT%" ^
  -TextB64 "%TEXT_B64%" ^
  -ExtraArgs "%EXTRA_ARGS% !TAIL_ARGS!"

set "EXIT_CODE=%ERRORLEVEL%"
echo.
echo 8-device ScanPen stress supervisor finished with exit code %EXIT_CODE%.
exit /b %EXIT_CODE%
