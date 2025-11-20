@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ================================
REM  decode_pickle_event.bat
REM  Pickle → JSON 変換ツール起動
REM ================================

REM === このbatのフォルダに移動 ===
pushd "%~dp0"

REM --- Python の相対パスを設定 ---
set "PYTHON_DIR=%~dp0..\python_embeded"
set "PYTHON=%PYTHON_DIR%\python.exe"
set "SCRIPT=%~dp0decode_pickle_event.py"

echo [DEBUG] Python path: %PYTHON%
echo [DEBUG] Script path: %SCRIPT%
echo.

REM --- Python 存在確認 ---
if not exist "%PYTHON%" (
    echo [ERROR] Python が見つかりません: "%PYTHON%"
    pause
    exit /b 1
)

REM --- スクリプト存在確認 ---
if not exist "%SCRIPT%" (
    echo [ERROR] decode_pickle_event.py が見つかりません: "%SCRIPT%"
    pause
    exit /b 1
)

REM --- Pickle ファイル入力（引数 or 手動入力） ---
if "%~1"=="" (
    echo デコードしたい pickle ファイルを入力してください:
    set /p TARGET="Path (.pkl) >>> "
) else (
    set "TARGET=%~1"
)

REM --- 入力チェック ---
if "%TARGET%"=="" (
    echo [ERROR] pickle ファイルが指定されていません
    pause
    exit /b 1
)

if not exist "%TARGET%" (
    echo [ERROR] 指定ファイルが存在しません: "%TARGET%"
    pause
    exit /b 1
)

echo.
echo ==== Pickle → JSON 変換を開始します ====
echo 入力: "%TARGET%"
echo.

REM --- 実行 ---
"%PYTHON%" "%SCRIPT%" "%TARGET%"

echo.
echo ==== JSON 変換が完了しました ====
pause

popd
endlocal
