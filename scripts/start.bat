@echo off
echo ====================================
echo パン屋原価計算アプリ起動スクリプト
echo ====================================
echo.

REM 仮想環境が存在するか確認
if not exist "venv\Scripts\activate.bat" (
    echo 仮想環境を作成中...
    python -m venv venv
    if errorlevel 1 (
        echo エラー: 仮想環境の作成に失敗しました
        echo Pythonがインストールされているか確認してください
        pause
        exit /b 1
    )
    echo 仮想環境を作成しました
    echo.
)

REM 仮想環境を有効化
echo 仮想環境を有効化中...
call venv\Scripts\activate.bat

REM 依存パッケージのインストール確認
echo 依存パッケージを確認中...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo 依存パッケージをインストール中...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo エラー: パッケージのインストールに失敗しました
        pause
        exit /b 1
    )
    echo パッケージのインストールが完了しました
    echo.
)

REM アプリケーションを起動
echo.
echo ====================================
echo アプリケーションを起動しています...
echo ====================================
echo.
echo ブラウザで以下のURLにアクセスしてください:
echo http://localhost:5000
echo.
echo 終了するには Ctrl+C を押してください
echo.

python run.py

pause
