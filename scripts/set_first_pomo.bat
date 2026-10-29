@echo off
rem Write tomorrow's first pomodoro for the 09:00 LINE notification.
rem Double-click (no arguments) to be prompted; or pass the text as arguments.
py -3 "%~dp0set_first_pomo.py" %*
if "%~1"=="" pause
