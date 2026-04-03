@echo off
color 0B
cd /d "%~dp0"

echo.
echo  ==========================================
echo   Seraphina PDF zu MP3
echo  ==========================================
echo.

python gui_smart.py

if errorlevel 1 (
    echo.
    echo  [FEHLER] Programm konnte nicht starten.
    echo  Stelle sicher, dass Python installiert ist:
    echo  pip install -r requirements.txt
    echo.
    pause
)
