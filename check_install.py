"""
インストール確認スクリプト
必要なパッケージがインストールされているか確認します
"""

import sys

def check_python_version():
    """Pythonバージョンの確認"""
    version = sys.version_info
    print(f"Python バージョン: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ エラー: Python 3.8以上が必要です")
        return False
    else:
        print("✓ Python バージョンOK")
        return True

def check_packages():
    """必要なパッケージの確認"""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_wtf',
        'wtforms',
        'bcrypt',
        'reportlab',
        'dotenv'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✓ {package} インストール済み")
        except ImportError:
            print(f"❌ {package} がインストールされていません")
            missing_packages.append(package)

    return len(missing_packages) == 0, missing_packages

def main():
    print("=" * 50)
    print("パン屋原価計算アプリ - インストール確認")
    print("=" * 50)
    print()

    # Pythonバージョン確認
    print("[1] Pythonバージョンを確認中...")
    python_ok = check_python_version()
    print()

    # パッケージ確認
    print("[2] 必要なパッケージを確認中...")
    packages_ok, missing = check_packages()
    print()

    # 結果表示
    print("=" * 50)
    if python_ok and packages_ok:
        print("✓ すべての確認が完了しました!")
        print()
        print("アプリケーションを起動するには:")
        print("  python run.py")
        print()
        print("または start.bat をダブルクリックしてください")
    else:
        print("❌ 問題が見つかりました")
        print()
        if not python_ok:
            print("Python 3.8以上をインストールしてください")
        if not packages_ok:
            print("以下のコマンドを実行してパッケージをインストールしてください:")
            print("  pip install -r requirements.txt")
    print("=" * 50)

if __name__ == '__main__':
    main()
