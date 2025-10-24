"""
材料テーブルのマイグレーションスクリプト
購入単位と使用単位のフィールドを追加
"""
import os
from app import create_app
from app.models import db, Ingredient
from sqlalchemy import text

def migrate_ingredients():
    """既存の材料データを新しいスキーマに移行"""
    app = create_app()

    with app.app_context():
        try:
            # 新しいカラムを追加（既に存在する場合はスキップ）
            with db.engine.connect() as conn:
                db_url = str(db.engine.url)

                # データベース種別に応じた処理
                if 'sqlite' in db_url:
                    # SQLiteの場合
                    result = conn.execute(text("PRAGMA table_info(ingredients)")).fetchall()
                    columns = [row[1] for row in result]
                elif 'postgresql' in db_url:
                    # PostgreSQLの場合
                    result = conn.execute(text("""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name='ingredients'
                    """)).fetchall()
                    columns = [row[0] for row in result]
                else:
                    print(f"Unknown database type: {db_url}")
                    return

                if 'purchase_price' not in columns:
                    print("Adding new columns to ingredients table...")

                    # 新しいカラムを追加（NULLable）
                    conn.execute(text("ALTER TABLE ingredients ADD COLUMN purchase_price NUMERIC(10, 2)"))
                    conn.execute(text("ALTER TABLE ingredients ADD COLUMN purchase_quantity NUMERIC(10, 3) DEFAULT 1"))
                    conn.execute(text("ALTER TABLE ingredients ADD COLUMN purchase_unit VARCHAR(20)"))
                    conn.execute(text("ALTER TABLE ingredients ADD COLUMN usage_unit VARCHAR(20)"))
                    conn.commit()

                    print("New columns added successfully")
                else:
                    print("Columns already exist, skipping column creation")

            # 既存のデータを新しいフィールドにマッピング
            ingredients = Ingredient.query.all()
            print(f"Found {len(ingredients)} ingredients to migrate")

            for ing in ingredients:
                # 既に新しいフィールドに値がある場合はスキップ
                if ing.purchase_price is not None:
                    continue

                # 旧フィールドから新フィールドにデータをコピー
                if ing.unit_price is not None:
                    ing.purchase_price = ing.unit_price
                    ing.purchase_quantity = 1  # デフォルト値
                    ing.purchase_unit = ing.unit if ing.unit else 'g'
                    ing.usage_unit = ing.unit if ing.unit else 'g'

                    print(f"Migrated: {ing.name} - {ing.unit_price}円/{ing.unit} -> {ing.purchase_price}円/{ing.purchase_quantity}{ing.purchase_unit} (使用単位: {ing.usage_unit})")

            db.session.commit()
            print(f"Successfully migrated {len(ingredients)} ingredients")

        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_ingredients()
