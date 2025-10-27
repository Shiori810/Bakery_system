"""
データベースマイグレーション: selling_priceカラムの追加
レシピテーブルに手動設定の販売価格フィールドを追加します
"""
import sqlite3
import sys
from pathlib import Path

def migrate_database():
    """selling_priceカラムをrecipesテーブルに追加"""

    # データベースファイルのパス
    db_path = Path(__file__).parent / 'instance' / 'bakery.db'

    if not db_path.exists():
        print(f"エラー: データベースファイルが見つかりません: {db_path}")
        return False

    try:
        print("=" * 60)
        print("データベースマイグレーション: selling_price追加")
        print("=" * 60)
        print(f"データベース: {db_path}")
        print()

        # データベース接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # カラムの存在確認
        cursor.execute("PRAGMA table_info(recipes)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'selling_price' in columns:
            print("[OK] selling_priceカラムは既に存在します。マイグレーション不要です。")
            conn.close()
            return True

        # カラムの追加
        print("selling_priceカラムを追加しています...")
        cursor.execute("""
            ALTER TABLE recipes
            ADD COLUMN selling_price NUMERIC(10, 2)
        """)

        conn.commit()
        print("[OK] selling_priceカラムを正常に追加しました。")
        print()

        # 確認
        cursor.execute("PRAGMA table_info(recipes)")
        columns_after = [row[1] for row in cursor.fetchall()]

        if 'selling_price' in columns_after:
            print("[OK] マイグレーションが正常に完了しました。")
            print()
            print("新しいフィールド:")
            print("  - selling_price: 手動設定の販売価格（NULL=推奨価格を使用）")
        else:
            print("[ERROR] マイグレーションに失敗しました。")
            conn.close()
            return False

        conn.close()
        return True

    except Exception as e:
        print(f"[ERROR] マイグレーション中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
