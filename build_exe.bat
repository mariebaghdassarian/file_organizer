@echo off
setlocal EnableDelayedExpansion
title File Organizer — Build .exe

echo ============================================================
echo   File Organizer  ^|  Build standalone .exe
echo ============================================================
echo.

REM ── 1. Install / upgrade PyInstaller ────────────────────────
echo [1/4] Installing PyInstaller...
pip install pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo ERROR: pip failed. Make sure Python is on your PATH.
    pause & exit /b 1
)

REM ── 2. Locate CustomTkinter assets ──────────────────────────
echo [2/4] Locating CustomTkinter assets...
for /f "delims=" %%i in (
    'python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))"'
) do set CTK_PATH=%%i

if "!CTK_PATH!"=="" (
    echo ERROR: Could not find CustomTkinter. Run: pip install customtkinter
    pause & exit /b 1
)
echo       Found: !CTK_PATH!
echo.

REM ── 3. Build ─────────────────────────────────────────────────
echo [3/4] Building executable (this takes a minute)...
echo.

pyinstaller ^
  --name "FileOrganizer" ^
  --onefile ^
  --windowed ^
  --add-data "file_icon.png;." ^
  --add-data "!CTK_PATH!;customtkinter" ^
  --hidden-import "PIL._tkinter_finder" ^
  --hidden-import "exifread" ^
  --hidden-import "pymediainfo" ^
  --noconfirm ^
  main.py

echo.

REM ── 4. Result ────────────────────────────────────────────────
echo [4/4] Done!
if exist "dist\FileOrganizer.exe" (
    echo.
    echo   ============================================================
    echo    SUCCESS — Your app is ready at:
    echo    dist\FileOrganizer.exe
    echo   ============================================================
    echo.
    echo   You can share this single file with anyone on Windows.
    echo   They do NOT need Python installed.
    echo.
    echo   IMPORTANT: For video date detection they must install MediaInfo:
    echo   https://mediaarea.net/en/MediaInfo/Download/Windows
) else (
    echo   Something went wrong — check the output above for errors.
)

echo.
pause
