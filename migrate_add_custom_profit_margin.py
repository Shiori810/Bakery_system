"""
データベースマイグレーションスクリプト: custom_profit_margin カラムを追加

このスクリプトは既存のデータベースにcustom_profit_marginカラムを追加します。
新規インストールの場合は、db.create_all()が自動的に正しいスキーマを作成するため、
このスクリプトを実行する必要はありません。
"""

import os
import sys
from sqlalchemy import create_engine, inspect, text

def migrate_database():
    """データベースにcustom_profit_marginカラムを追加"""

    # DATABASE_URLの取得
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/bakery.db')

    # PostgreSQL URLの修正
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print(f"データベース接続: {database_url}")

    try:
        # エンジンを作成
        engine = create_engine(database_url)

        # テーブルが存在するか確認
        inspector = inspect(engine)
        if 'recipes' not in inspector.get_table_names():
            print("エラー: recipesテーブルが見つかりません。")
            print("先にアプリケーションを起動してデータベースを初期化してください。")
            return False

        # カラムが既に存在するか確認
        columns = [col['name'] for col in inspector.get_columns('recipes')]

        if 'custom_profit_margin' in columns:
            print("custom_profit_marginカラムは既に存在します。マイグレーション不要です。")
            return True

        print("custom_profit_marginカラムを追加しています...")

        # カラムを追加
        with engine.connect() as connection:
            # SQLiteとPostgreSQLで構文が異なる可能性があるため条件分岐
            if database_url.startswith('sqlite'):
                connection.execute(text(
                    "ALTER TABLE recipes ADD COLUMN custom_profit_margin NUMERIC(5, 2)"
                ))
            else:  # PostgreSQL
                connection.execute(text(
                    "ALTER TABLE recipes ADD COLUMN custom_profit_margin NUMERIC(5, 2)"
                ))
            connection.commit()

        print("[OK] マイグレーション完了: custom_profit_marginカラムを追加しました。")
        print("  既存のレシピは基本設定の利益率を使用します（custom_profit_margin = NULL）")
        return True

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("データベースマイグレーション: custom_profit_margin追加")
    print("=" * 60)

    success = migrate_database()

    if success:
        print("\n[OK] マイグレーションが正常に完了しました。")
        sys.exit(0)
    else:
        print("\n[ERROR] マイグレーションに失敗しました。")
        sys.exit(1)
