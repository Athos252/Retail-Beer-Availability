@echo off

:: Change directory to your project directory
cd /D "G:\Dastardly Projects"

:: Set path to python script
set SCRIPT_PATH=scraper.py

:: Set path to the Scripts directory in your venv
set VENV_SCRIPTS_PATH=venv\Scripts

:: Activate virtual environment
echo Activating virtual environment...
call %VENV_SCRIPTS_PATH%\activate.bat

:: Run python script with command-line arguments
echo Running Python script...
%VENV_SCRIPTS_PATH%\python %SCRIPT_PATH% 1 +1
