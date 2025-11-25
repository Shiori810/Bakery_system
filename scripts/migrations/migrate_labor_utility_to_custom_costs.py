"""
データベースマイグレーション: 人件費・光熱費をCustomCostItemに移行

CostSettingテーブルの人件費・光熱費フィールドを、
CustomCostItem管理システムに移行します。

実行前に必ずバックアップを取ってください。
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

def migrate_database():
    """人件費・光熱費をCustomCostItemに移行"""

    # DATABASE_URLの取得
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/bakery.db')

    # RenderのPostgreSQLは postgres:// で始まるが、SQLAlchemyは postgresql:// が必要
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print("=" * 70)
    print("データベースマイグレーション: 人件費・光熱費のCustomCostItem化")
    print("=" * 70)
    print(f"データベース接続: {database_url.split('@')[0] if '@' in database_url else 'SQLite'}@...")
    print()

    try:
        # エンジンを作成
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # テーブルが存在するか確認
        inspector = inspect(engine)
        if 'cost_settings' not in inspector.get_table_names():
            print("エラー: cost_settingsテーブルが見つかりません。")
            return False

        if 'custom_cost_items' not in inspector.get_table_names():
            print("エラー: custom_cost_itemsテーブルが見つかりません。")
            return False

        # ステップ1: CostSettingから人件費・光熱費データを読み取る
        print("ステップ1: 既存の人件費・光熱費設定を読み取り中...")
        print()

        # CostSettingテーブルから全店舗のデータを取得
        result = session.execute(text("""
            SELECT id, store_id, include_labor_cost, include_utility_cost,
                   hourly_wage, monthly_utility_cost
            FROM cost_settings
        """))

        cost_settings = result.fetchall()
        print(f"[OK] {len(cost_settings)}店舗の設定を取得しました")
        print()

        # ステップ2: CustomCostItemを作成
        print("ステップ2: CustomCostItemレコードを作成中...")
        print()

        labor_count = 0
        utility_count = 0
        skip_count = 0

        for setting in cost_settings:
            setting_id, store_id, include_labor, include_utility, hourly_wage, monthly_utility = setting

            # 既存のCustomCostItemをチェック
            existing_labor = session.execute(text("""
                SELECT id FROM custom_cost_items
                WHERE store_id = :store_id AND name = '人件費'
            """), {'store_id': store_id}).fetchone()

            existing_utility = session.execute(text("""
                SELECT id FROM custom_cost_items
                WHERE store_id = :store_id AND name = '光熱費'
            """), {'store_id': store_id}).fetchone()

            # 人件費の処理
            if hourly_wage and float(hourly_wage) > 0:
                if existing_labor:
                    print(f"  [SKIP] 店舗ID {store_id}: 「人件費」は既に存在します")
                    skip_count += 1
                else:
                    # 時給を分単価に変換: hourly_wage / 60
                    per_minute_labor = float(hourly_wage) / 60.0
                    is_active = bool(include_labor) if include_labor is not None else False

                    session.execute(text("""
                        INSERT INTO custom_cost_items
                        (store_id, name, calculation_type, amount, is_active, description, display_order)
                        VALUES (:store_id, :name, :calc_type, :amount, :is_active, :description, :order)
                    """), {
                        'store_id': store_id,
                        'name': '人件費',
                        'calc_type': 'per_time',
                        'amount': per_minute_labor,
                        'is_active': is_active,
                        'description': f'時給{hourly_wage}円から自動変換（{per_minute_labor:.2f}円/分）',
                        'order': 1
                    })

                    status = "有効" if is_active else "無効"
                    print(f"  [作成] 店舗ID {store_id}: 人件費 {per_minute_labor:.2f}円/分 ({status})")
                    labor_count += 1

            # 光熱費の処理
            if monthly_utility and float(monthly_utility) > 0:
                if existing_utility:
                    print(f"  [SKIP] 店舗ID {store_id}: 「光熱費」は既に存在します")
                    skip_count += 1
                else:
                    # 月額を分単価に変換: monthly_utility / 30 / 24 / 60 = monthly_utility / 43200
                    per_minute_utility = float(monthly_utility) / 43200.0
                    is_active = bool(include_utility) if include_utility is not None else False

                    session.execute(text("""
                        INSERT INTO custom_cost_items
                        (store_id, name, calculation_type, amount, is_active, description, display_order)
                        VALUES (:store_id, :name, :calc_type, :amount, :is_active, :description, :order)
                    """), {
                        'store_id': store_id,
                        'name': '光熱費',
                        'calc_type': 'per_time',
                        'amount': per_minute_utility,
                        'is_active': is_active,
                        'description': f'月額{monthly_utility}円から自動変換（{per_minute_utility:.4f}円/分）',
                        'order': 2
                    })

                    status = "有効" if is_active else "無効"
                    print(f"  [作成] 店舗ID {store_id}: 光熱費 {per_minute_utility:.4f}円/分 ({status})")
                    utility_count += 1

        session.commit()
        print()
        print(f"[OK] CustomCostItem作成完了:")
        print(f"  - 人件費: {labor_count}件")
        print(f"  - 光熱費: {utility_count}件")
        print(f"  - スキップ: {skip_count}件")
        print()

        # ステップ3: CostSettingテーブルからカラムを削除
        print("ステップ3: CostSettingテーブルから旧フィールドを削除中...")
        print()

        # カラムが存在するか確認
        columns = [col['name'] for col in inspector.get_columns('cost_settings')]

        columns_to_drop = []
        if 'include_labor_cost' in columns:
            columns_to_drop.append('include_labor_cost')
        if 'include_utility_cost' in columns:
            columns_to_drop.append('include_utility_cost')
        if 'hourly_wage' in columns:
            columns_to_drop.append('hourly_wage')
        if 'monthly_utility_cost' in columns:
            columns_to_drop.append('monthly_utility_cost')

        if not columns_to_drop:
            print("[OK] 削除対象のカラムは既に存在しません。マイグレーション済みです。")
            return True

        # データベースによって構文が異なるため分岐
        db_type = 'postgresql' if 'postgresql' in database_url else 'sqlite'

        if db_type == 'sqlite':
            # SQLiteはALTER TABLE DROP COLUMNをサポートしないため、テーブルを再作成
            print("  [INFO] SQLiteの制約により、テーブルを再作成します...")

            # 新しいテーブルを作成
            session.execute(text("""
                CREATE TABLE cost_settings_new (
                    id INTEGER PRIMARY KEY,
                    store_id INTEGER NOT NULL UNIQUE,
                    profit_margin NUMERIC(5, 2) DEFAULT 30.0,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (store_id) REFERENCES stores(id)
                )
            """))

            # データをコピー
            session.execute(text("""
                INSERT INTO cost_settings_new (id, store_id, profit_margin, created_at, updated_at)
                SELECT id, store_id, profit_margin, created_at, updated_at
                FROM cost_settings
            """))

            # 旧テーブルを削除
            session.execute(text("DROP TABLE cost_settings"))

            # 新テーブルをリネーム
            session.execute(text("ALTER TABLE cost_settings_new RENAME TO cost_settings"))

            print("  [OK] SQLite: テーブル再作成完了")

        else:
            # PostgreSQLはALTER TABLE DROP COLUMNをサポート
            for column in columns_to_drop:
                session.execute(text(f"ALTER TABLE cost_settings DROP COLUMN {column}"))
                print(f"  [削除] {column}")

            print("  [OK] PostgreSQL: カラム削除完了")

        session.commit()
        print()

        # 完了メッセージ
        print("=" * 70)
        print("[OK] マイグレーションが正常に完了しました！")
        print("=" * 70)
        print()
        print("変更内容:")
        print(f"  1. {labor_count}件の人件費をCustomCostItemに移行")
        print(f"  2. {utility_count}件の光熱費をCustomCostItemに移行")
        print(f"  3. CostSettingテーブルから4つのカラムを削除")
        print()
        print("次のステップ:")
        print("  - アプリケーションを再起動")
        print("  - 設定画面で利益率設定を確認")
        print("  - カスタム原価項目管理で人件費・光熱費を確認")
        print("  - レシピ詳細画面で原価計算が正しいか確認")
        print()

        session.close()
        return True

    except Exception as e:
        print(f"[ERROR] マイグレーション中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

if __name__ == '__main__':
    print()
    print("警告: このマイグレーションは以下の変更を行います:")
    print("  1. 人件費・光熱費をCustomCostItemとして作成")
    print("  2. CostSettingテーブルから以下のカラムを削除:")
    print("     - include_labor_cost")
    print("     - include_utility_cost")
    print("     - hourly_wage")
    print("     - monthly_utility_cost")
    print()
    print("実行前に必ずバックアップを取ることを推奨します。")
    print()

    response = input("続行しますか？ (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("マイグレーションをキャンセルしました。")
        sys.exit(0)

    print()
    success = migrate_database()
    sys.exit(0 if success else 1)
