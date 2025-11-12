@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM === このbatのフォルダに移動 ===
pushd "%~dp0"

REM --- 上の階層のPythonフォルダを指定 ---
set "PYTHON_DIR=%~dp0..\python_embeded"
set "PYTHON=%PYTHON_DIR%\python.exe"
set "SCRIPT=%~dp0image_to_shape.py"

echo [DEBUG] Python path: %PYTHON%
echo [DEBUG] Script path: %SCRIPT%
echo.

REM --- 存在確認 ---
if not exist "%PYTHON%" (
    echo [ERROR] Python が見つかりません: "%PYTHON%"
    pause
    exit /b 1
)
if not exist "%SCRIPT%" (
    echo [ERROR] スクリプトが見つかりません: "%SCRIPT%"
    pause
    exit /b 1
)

REM --- 実行 ---
echo ==== 画像→形状JSON変換を開始します... ====
"%PYTHON%" "%SCRIPT%"

echo ==== 完了 ====
pause
popd
endlocal
