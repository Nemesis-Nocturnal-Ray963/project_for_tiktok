@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM === このbatのフォルダに移動 ===
pushd "%~dp0"

REM --- 上の階層のPythonフォルダを指定 ---
set "PYTHON_DIR=%~dp0..\python_embeded"
set "PYTHON=%PYTHON_DIR%\python.exe"
set "SCRIPT=%~dp0export_viewer_logs_to_html.py"

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
    echo [ERROR] HTML変換スクリプトが見つかりません: "%SCRIPT%"
    pause
    exit /b 1
)

REM --- 実行 ---
echo ==== 視聴者ログ → HTML レポート生成を開始します... ====
"%PYTHON%" "%SCRIPT%"

echo ==== HTMLレポート生成が完了しました ====
pause
popd
endlocal
