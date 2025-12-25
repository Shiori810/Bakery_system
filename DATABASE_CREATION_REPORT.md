# データベース作成レポート

## 概要

このアプリケーションでは、**SQLAlchemy ORM**と**Flask-SQLAlchemy**を使用してデータベースを管理しています。データベースの作成は主に自動化されており、手動でのSQL実行は不要です。

---

## データベース作成の仕組み

### 1. 初期作成（自動）

データベースは**アプリケーションの初回起動時に自動的に作成**されます。

#### 作成プロセス

**ファイル**: [app/__init__.py:74-76](app/__init__.py#L74-L76)

```python
# データベーステーブル作成
with app.app_context():
    db.create_all()
```

**実行タイミング**:
- `run.py`を実行してアプリケーションを起動したとき
- `create_app()`関数が呼ばれ、その中で`db.create_all()`が実行される

**動作内容**:
1. [app/models.py](app/models.py)で定義されたすべてのモデルクラスを読み込む
2. SQLAlchemyが自動的にテーブル作成のSQLを生成
3. データベースファイル（SQLite）またはPostgreSQLサーバーに接続
4. テーブルが存在しない場合のみ作成（既存テーブルは変更しない）

---

### 2. データベースの種類

#### 開発環境: SQLite

**場所**: `instance/bakery.db`

**設定**: [app/__init__.py:12](app/__init__.py#L12)

```python
database_url = os.environ.get('DATABASE_URL', 'sqlite:///bakery.db')
```

**特徴**:
- ファイルベースのデータベース
- インストール不要
- 単一ファイルで管理が簡単
- 開発・テスト用途に最適

**確認方法**:
```bash
# データベースファイルの存在確認
ls instance/bakery.db

# テーブル一覧の確認
python -c "import sqlite3; conn = sqlite3.connect('instance/bakery.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print('\n'.join([t[0] for t in cursor.fetchall()]))"
```

#### 本番環境: PostgreSQL

**場所**: Render.com のマネージドPostgreSQLサービス

**URL**: `https://bakery-system.onrender.com`

**設定**: 環境変数`DATABASE_URL`で指定

**特徴**:
- 高パフォーマンス
- 複数ユーザーの同時接続に対応
- トランザクションの信頼性が高い
- 本番運用に最適

---

## データベーススキーマ

### テーブル一覧

現在のデータベースには以下の6つのテーブルが存在します:

| テーブル名 | 説明 | 定義場所 |
|-----------|------|---------|
| `stores` | 店舗情報（ユーザーアカウント） | [models.py:9-34](app/models.py#L9-L34) |
| `cost_settings` | 原価計算設定（利益率） | [models.py:37-48](app/models.py#L37-L48) |
| `ingredients` | 材料マスタ | [models.py:51-152](app/models.py#L51-L152) |
| `recipes` | レシピ情報 | [models.py:155-240](app/models.py#L155-L240) |
| `recipe_ingredients` | レシピと材料の中間テーブル | [models.py:243-258](app/models.py#L243-L258) |
| `custom_cost_items` | カスタム原価項目（人件費・光熱費等） | [models.py:261-306](app/models.py#L261-L306) |

### ER図（関係図）

```
stores (店舗)
  ├── cost_settings (原価設定) [1:1]
  ├── ingredients (材料) [1:多]
  ├── recipes (レシピ) [1:多]
  └── custom_cost_items (原価項目) [1:多]

recipes (レシピ)
  └── recipe_ingredients (使用材料) [1:多]
      └── ingredients (材料) [多:1]
```

---

## スキーマの進化（マイグレーション）

アプリケーションの機能追加に伴い、データベーススキーマも進化してきました。既存データを保持したままテーブル構造を変更するため、**マイグレーションスクリプト**が用意されています。

### マイグレーション履歴

#### 1. 材料テーブルの拡張

**実行日**: v1.1.0リリース時

**ファイル**: [scripts/migrations/migrate_ingredients.py](scripts/migrations/migrate_ingredients.py)

**変更内容**:
- `purchase_price` (購入価格)
- `purchase_quantity` (購入数量)
- `purchase_unit` (購入単位: kg, L等)
- `usage_unit` (使用単位: g, ml等)

**目的**: 購入単位と使用単位の自動変換機能を実装

**実行方法**:
```bash
python scripts/migrations/migrate_ingredients.py
```

---

#### 2. 販売価格フィールドの追加

**実行日**: v1.1.0リリース時

**ファイル**: [scripts/migrations/migrate_add_selling_price.py](scripts/migrations/migrate_add_selling_price.py)

**変更内容**:
- `recipes.selling_price` (手動設定の販売価格)

**目的**: 推奨価格の代わりに手動で販売価格を設定できるようにする

**実行方法**:
```bash
python scripts/migrations/migrate_add_selling_price.py
```

---

#### 3. 商品ごと利益率の追加

**実行日**: 最新機能追加時

**ファイル**: [scripts/migrations/migrate_add_custom_profit_margin.py](scripts/migrations/migrate_add_custom_profit_margin.py)

**変更内容**:
- `recipes.custom_profit_margin` (商品ごとの利益率)

**目的**: 商品ごとに異なる利益率を設定できるようにする

**実行方法**:
```bash
python scripts/migrations/migrate_add_custom_profit_margin.py
```

---

#### 4. 人件費・光熱費のカスタム原価項目化

**実行日**: カスタム原価項目機能追加時

**ファイル**: [scripts/migrations/migrate_labor_utility_to_custom_costs.py](scripts/migrations/migrate_labor_utility_to_custom_costs.py)

**変更内容**:
- `cost_settings`テーブルから以下のカラムを削除:
  - `include_labor_cost`
  - `include_utility_cost`
  - `hourly_wage`
  - `monthly_utility_cost`
- `custom_cost_items`テーブルに人件費・光熱費を移行

**目的**: より柔軟な原価項目管理システムへの移行

**実行方法**:
```bash
python scripts/migrations/migrate_labor_utility_to_custom_costs.py
```

**注意**: このマイグレーションは破壊的変更のため、実行前に確認プロンプトが表示されます

---

## マイグレーションの仕組み

### 共通パターン

すべてのマイグレーションスクリプトは以下の共通パターンに従っています:

1. **カラムの存在確認**
   ```python
   inspector = inspect(engine)
   columns = [col['name'] for col in inspector.get_columns('table_name')]

   if 'new_column' in columns:
       print("カラムは既に存在します")
       return True
   ```

2. **ALTER TABLE実行**
   ```python
   connection.execute(text(
       "ALTER TABLE table_name ADD COLUMN new_column TYPE"
   ))
   connection.commit()
   ```

3. **データベース種別の考慮**
   - SQLite: カラム削除非対応のため、テーブル再作成が必要
   - PostgreSQL: ALTER TABLE DROP COLUMNをサポート

4. **エラーハンドリング**
   ```python
   try:
       # マイグレーション処理
       connection.commit()
   except Exception as e:
       connection.rollback()
       print(f"エラー: {e}")
   ```

---

## データベースの初期化・リセット

### 開発環境（SQLite）

```bash
# データベースファイルを削除
rm instance/bakery.db

# アプリケーションを起動（自動再作成）
python run.py
```

### 本番環境（PostgreSQL）

```bash
# PostgreSQLに接続
psql $DATABASE_URL

# テーブルを削除
DROP TABLE recipe_ingredients CASCADE;
DROP TABLE recipes CASCADE;
DROP TABLE ingredients CASCADE;
DROP TABLE custom_cost_items CASCADE;
DROP TABLE cost_settings CASCADE;
DROP TABLE stores CASCADE;

# アプリケーションを再起動（自動再作成）
```

**注意**: 本番環境でのリセットは全データが消えるため、必ずバックアップを取ってから実行してください。

---

## セットアップ手順（新規インストール）

### ステップ1: 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# SQLiteを使用する場合（デフォルト）
# DATABASE_URLの設定は不要

# PostgreSQLを使用する場合
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

### ステップ2: 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### ステップ3: データベースの自動作成

```bash
# アプリケーションを起動
python run.py

# ✓ instance/bakery.dbが自動作成される
# ✓ すべてのテーブルが自動作成される
```

### ステップ4: 初期データの登録

ブラウザで`http://localhost:5000`にアクセスし:

1. 店舗登録ページで新規アカウントを作成
2. ログイン後、設定画面で利益率などを設定
3. 材料マスタを登録
4. レシピを作成

**すべてGUIから実行可能** - SQLの知識は不要です。

---

## 既存データベースへのマイグレーション

古いバージョンからアップグレードする場合:

```bash
# 1. バックアップを取る
cp instance/bakery.db instance/bakery.db.backup

# 2. 必要なマイグレーションを順番に実行
python scripts/migrations/migrate_ingredients.py
python scripts/migrations/migrate_add_selling_price.py
python scripts/migrations/migrate_add_custom_profit_margin.py
python scripts/migrations/migrate_labor_utility_to_custom_costs.py

# 3. アプリケーションを起動
python run.py
```

**重要**: マイグレーションは順番に実行する必要があります。スキップすると依存関係のエラーが発生する可能性があります。

---

## データベース管理のベストプラクティス

### 1. 開発時

- SQLiteを使用（設定不要で簡単）
- `instance/bakery.db`をgitignoreに追加（個人データの保護）
- テストデータは適宜削除・再作成

### 2. 本番運用時

- PostgreSQLを使用（パフォーマンスと信頼性）
- 定期的なバックアップを実施
- マイグレーション前に必ずバックアップ
- 環境変数でDATABASE_URLを管理

### 3. スキーマ変更時

- [app/models.py](app/models.py)でモデルを変更
- マイグレーションスクリプトを作成
- 既存データの互換性を考慮
- ロールバック手順を用意

---

## トラブルシューティング

### エラー: "no such table: stores"

**原因**: データベースが初期化されていない

**解決方法**:
```bash
# データベースファイルを削除して再作成
rm instance/bakery.db
python run.py
```

---

### エラー: "column not found"

**原因**: マイグレーションが未実行

**解決方法**:
```bash
# 必要なマイグレーションを実行
python scripts/migrations/migrate_XXX.py
```

---

### エラー: "database is locked"

**原因**: SQLiteが複数プロセスから同時アクセスされている

**解決方法**:
```bash
# アプリケーションをすべて停止してから再起動
# または PostgreSQLに移行を検討
```

---

## まとめ

このアプリケーションのデータベース作成は以下の特徴があります:

1. **完全自動化** - 手動でのSQLファイル実行は不要
2. **ORM駆動** - models.pyの定義から自動生成
3. **段階的進化** - マイグレーションスクリプトで既存データを保護
4. **環境適応** - SQLite（開発）とPostgreSQL（本番）の両対応
5. **開発者フレンドリー** - SQLの知識がなくても利用可能

データベースの作成・管理はすべてPythonコードとFlask-SQLAlchemyで自動化されており、開発者はビジネスロジックに集中できる設計になっています。
