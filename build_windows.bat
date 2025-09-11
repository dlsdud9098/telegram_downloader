@echo off
echo Building Telegram Auto Downloader for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Build executable
echo.
echo Building executable...
pyinstaller --onefile ^
    --console ^
    --name TelegramAutoDownloader ^
    --add-data "images;images" ^
    --add-data "README.md;." ^
    --hidden-import PIL._tkinter_finder ^
    --hidden-import customtkinter ^
    --hidden-import cv2 ^
    --hidden-import numpy ^
    --hidden-import mss ^
    --hidden-import pyautogui ^
    --hidden-import pynput ^
    --hidden-import pynput.keyboard._win32 ^
    --hidden-import pynput.mouse._win32 ^
    --hidden-import win32gui ^
    --hidden-import win32api ^
    --hidden-import win32con ^
    main.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable created: dist\TelegramAutoDownloader.exe
echo.
echo Creating distribution folder...

REM Create distribution folder
if exist telegram_downloader_windows rmdir /s /q telegram_downloader_windows
mkdir telegram_downloader_windows

REM Copy files
copy dist\TelegramAutoDownloader.exe telegram_downloader_windows\
xcopy /e /i images telegram_downloader_windows\images
copy README.md telegram_downloader_windows\

echo.
echo Distribution folder created: telegram_downloader_windows
echo.
echo You can now:
echo 1. Copy the telegram_downloader_windows folder to any Windows PC
echo 2. Run TelegramAutoDownloader.exe
echo.
pause