@echo off
REM Phoenix-Live daily crawler + push (V2.9.17-P1.5 _safe_crawl.py + absolute python path)
REM Fixed: schtasks triggers cmd.exe without user PATH, so 'python' is not found
REM Fix: use %LOCALAPPDATA%\Programs\Python\Python313\python.exe directly
REM Switch: crawler\run.py -> crawler\_safe_crawl.py (P1.5 baseline protection)

setlocal

set PHOENIX_ROOT=D:\MINIMAX\phoenix-live
set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
set LOG=%PHOENIX_ROOT%\logs\scheduled.log

cd /d %PHOENIX_ROOT%

echo [%date% %time%] START daily crawler (safe_crawl) >> %LOG%

"%PYTHON_EXE%" crawler\_safe_crawl.py 1>>%LOG% 2>&1

if %ERRORLEVEL% NEQ 0 (
  echo [%date% %time%] FAILED with code %ERRORLEVEL% >> %LOG%
  exit /b 1
)

echo [%date% %time%] DONE >> %LOG%
endlocal
