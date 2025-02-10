@echo off
cd /d "%~dp0"
echo Activating virtual environment...
call myenv\Scripts\activate.bat
echo Running the program...
python NonPlainarSlicing\main.py
pause