@echo off
cd /d "%~dp0"
python -m venv myenv
echo Activating virtual environment...
call myenv\Scripts\activate.bat
python -m pip install -r requirements.txt
echo Running the program...
python NonPlainarSlicing\main.py
pause