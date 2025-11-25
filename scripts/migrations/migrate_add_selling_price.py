"""
データベースマイグレーション: selling_priceカラムの追加
レシピテーブルに手動設定の販売価格フィールドを追加します
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text

def migrate_database():
    """selling_priceカラムをrecipesテーブルに追加"""

    # DATABASE_URLの取得
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/bakery.db')

    # RenderのPostgreSQLは postgres:// で始まるが、SQLAlchemyは postgresql:// が必要
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print("=" * 60)
    print("データベースマイグレーション: selling_price追加")
    print("=" * 60)
    print(f"データベース接続: {database_url.split('@')[0]}@...")
    print()

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

        if 'selling_price' in columns:
            print("[OK] selling_priceカラムは既に存在します。マイグレーション不要です。")
            return True

        print("selling_priceカラムを追加しています...")

        # カラムを追加
        with engine.connect() as connection:
            # SQLiteとPostgreSQLで構文が同じなので統一
            connection.execute(text(
                "ALTER TABLE recipes ADD COLUMN selling_price NUMERIC(10, 2)"
            ))
            connection.commit()

        print("[OK] selling_priceカラムを正常に追加しました。")
        print()
        print("新しいフィールド:")
        print("  - selling_price: 手動設定の販売価格（NULL=推奨価格を使用）")
        print()
        print("[OK] マイグレーションが正常に完了しました。")
        return True

    except Exception as e:
        print(f"[ERROR] マイグレーション中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
