
@ECHO OFF

start console -w "DEMO PYPS" -d "%~dp0"
start console -w "GIT PYPS" -d "%~dp0"
start console -w "SPHINX PYPS" -d "%~dp0"

start cmd /c cd "%~dp0" ^&^& start gvim -p -c ":simalt ~x"

if "%PYTHON_HOME%"=="" GOTO NO_HH
    start hh "%PYTHON_HOME%.\Lib\site-packages\PyWin32.chm"
:NO_HH
