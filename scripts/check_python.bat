@echo off
echo ============================================
echo Python環境チェックツール
echo ============================================
echo.

echo [確認1] python コマンド
python --version 2>nul
if %errorlevel% equ 0 (
    echo ✓ python コマンドが使えます
    python --version
) else (
    echo ❌ python コマンドが使えません
)
echo.

echo [確認2] py コマンド
py --version 2>nul
if %errorlevel% equ 0 (
    echo ✓ py コマンドが使えます
    py --version
) else (
    echo ❌ py コマンドが使えません
)
echo.

echo [確認3] python3 コマンド
python3 --version 2>nul
if %errorlevel% equ 0 (
    echo ✓ python3 コマンドが使えます
    python3 --version
) else (
    echo ❌ python3 コマンドが使えません
)
echo.

echo [確認4] pip コマンド
pip --version 2>nul
if %errorlevel% equ 0 (
    echo ✓ pip コマンドが使えます
    pip --version
) else (
    echo ❌ pip コマンドが使えません
)
echo.

echo ============================================
echo 診断結果
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% equ 0 goto :python_ok

py --version >nul 2>&1
if %errorlevel% equ 0 goto :py_ok

python3 --version >nul 2>&1
if %errorlevel% equ 0 goto :python3_ok

echo ❌ Pythonがインストールされていません
echo.
echo 対処法:
echo 1. https://www.python.org/downloads/ にアクセス
echo 2. 最新版のPythonをダウンロード
echo 3. インストール時に「Add Python to PATH」にチェック
echo 4. インストール後、コマンドプロンプトを再起動
echo 5. このスクリプトを再実行
echo.
goto :end

:python_ok
echo ✓ Python環境は正常です
echo.
echo 次のステップ:
echo   simple_start.bat をダブルクリックしてアプリを起動
echo.
goto :end

:py_ok
echo ✓ Python環境は正常です（pyコマンド）
echo.
echo 次のステップ:
echo   simple_start.bat をダブルクリックしてアプリを起動
echo.
goto :end

:python3_ok
echo ✓ Python環境は正常です（python3コマンド）
echo.
echo 次のステップ:
echo   simple_start.bat をダブルクリックしてアプリを起動
echo.
goto :end

:end
echo ============================================
pause
