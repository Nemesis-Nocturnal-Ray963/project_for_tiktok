@echo on
chcp 65001 > nul
setlocal

REM --- Pythonフォルダ指定（相対パスで） ---
set PYTHON_DIR=%~dp0python_embeded
set PYTHON=%PYTHON_DIR%\python.exe


REM --- アプリ起動 ---
echo ==== アプリを起動します... ====
%PYTHON% main.py

pause
endlocal