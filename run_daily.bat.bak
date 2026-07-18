@echo off
REM Phoenix-Live daily crawler + push (ASCII only to avoid GBK issues)
REM Tokens are loaded from .env (gitignored) - do NOT hardcode them here.

set PHOENIX_ROOT=D:\MINIMAX\phoenix-live
cd /d %PHOENIX_ROOT%

REM Load .env into environment
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
  set %%a=%%b
)

echo [%date% %time%] START daily crawler >> logs\scheduled.log

python crawler\run.py 1>>logs\scheduled.log 2>&1

if %ERRORLEVEL% NEQ 0 (
  echo [%date% %time%] FAILED with code %ERRORLEVEL% >> logs\scheduled.log
  exit /b 1
)

echo [%date% %time%] DONE >> logs\scheduled.log
