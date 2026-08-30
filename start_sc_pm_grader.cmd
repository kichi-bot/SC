@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_sc_pm_grader.ps1"
set "launcherExit=%errorlevel%"
if not "%launcherExit%"=="0" (
  echo.
  echo Could not start the SC written-answer grader.
  echo Please report the message above to Codex.
  pause
)
exit /b %launcherExit%
