@ECHO OFF

start console -w "PYPS DEMO" -d "%~dp0"
start console -w "PYPS GIT" -d "%~dp0"

start cmd /c cd "%~dp0" ^&^& start gvim -p -c ":simalt ~x"

if "%PYTHON_HOME%"=="" GOTO NO_HH
    start hh "%PYTHON_HOME%.\Lib\site-packages\PyWin32.chm"
:NO_HH

