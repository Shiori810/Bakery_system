@echo off
echo ============================================
echo パン屋原価計算アプリ - 簡易起動スクリプト
echo ============================================
echo.

REM Pythonコマンドの確認
echo [1/3] Python環境を確認中...

REM python コマンドを試す
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :found_python
)

REM py コマンドを試す
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :found_python
)

REM python3 コマンドを試す
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto :found_python
)

REM Pythonが見つからない場合
echo.
echo ❌ エラー: Pythonが見つかりません
echo.
echo Pythonをインストールしてください:
echo https://www.python.org/downloads/
echo.
echo インストール時の注意:
echo - 「Add Python to PATH」にチェックを入れてください
echo.
pause
exit /b 1

:found_python
echo ✓ Python が見つかりました: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM 依存パッケージのインストール
echo [2/3] 必要なパッケージをインストール中...
echo （初回は数分かかります。お待ちください...）
echo.

%PYTHON_CMD% -m pip install --quiet Flask Flask-SQLAlchemy Flask-Login Flask-WTF WTForms bcrypt reportlab python-dotenv email-validator

if %errorlevel% neq 0 (
    echo.
    echo ⚠ 警告: 一部のパッケージのインストールに失敗しました
    echo それでも起動を試みます...
    echo.
)

echo ✓ パッケージのインストール完了
echo.

REM アプリケーションを起動
echo [3/3] アプリケーションを起動中...
echo.
echo ============================================
echo アプリケーションが起動しました！
echo ============================================
echo.
echo ブラウザで以下のURLを開いてください:
echo.
echo   http://localhost:5000
echo.
echo 終了するには Ctrl+C を押してください
echo ============================================
echo.

%PYTHON_CMD% run.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ アプリケーションの起動に失敗しました
    echo.
    echo エラーの原因を確認してください。
    echo.
)

pause
