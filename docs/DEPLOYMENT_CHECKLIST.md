# Webデプロイ チェックリスト

## 現在の状況

**日時**: 2025-10-28
**最終コミット**: a35b54f
**デプロイ先**: Render (https://bakery-cost-calculator.onrender.com)

---

## 実行が必要なマイグレーション

pullした最新コードには、以下の3つのマイグレーションスクリプトが含まれています：

### 1. migrate_ingredients.py（材料テーブルの更新）
**目的**: 購入単位と使用単位のフィールドを追加

**追加されるカラム**:
- `purchase_price` - 購入価格
- `purchase_quantity` - 購入数量
- `purchase_unit` - 購入単位
- `usage_unit` - 使用単位

**影響**: 材料マスタの管理方法が大幅に改善（購入単位と使用単位を分離）

### 2. migrate_add_selling_price.py（販売価格フィールドの追加）
**目的**: レシピに手動設定の販売価格フィールドを追加

**追加されるカラム**:
- `selling_price` - 販売価格（手動設定）

**影響**: 販売推奨価格ではなく、手動で販売価格を設定可能に

### 3. migrate_add_custom_profit_margin.py（商品ごとの利益率）
**目的**: 商品ごとに個別の利益率を設定

**追加されるカラム**:
- `custom_profit_margin` - 商品ごとの利益率

**影響**: 商品ごとに異なる利益率を設定可能

---

## デプロイ手順

### ステップ1: Renderでの自動デプロイ確認

GitHubにプッシュ済みのため、Renderが自動的に再デプロイを開始しているはずです。

**確認方法**:
1. https://dashboard.render.com/ にログイン
2. `bakery-cost-calculator` サービスを選択
3. **Events** タブで最新のデプロイ状況を確認

**期待される状態**:
- 最新のコミット `a35b54f` がデプロイ中または完了

---

### ステップ2: Renderシェルでマイグレーションを実行

デプロイ完了後、以下のマイグレーションを**順番に**実行する必要があります。

#### 2.1 Renderシェルへのアクセス

1. Renderダッシュボードで `bakery-cost-calculator` を選択
2. 右上の **"Shell"** ボタンをクリック
3. ターミナルが開きます

#### 2.2 マイグレーション実行（順番が重要）

**順番1: 材料テーブルのマイグレーション**
```bash
python migrate_ingredients.py
```

**期待される出力**:
```
Adding new columns to ingredients table...
New columns added successfully
Found X ingredients to migrate
Migrated: 材料名 - 価格円/単位 -> 購入価格円/購入数量購入単位 (使用単位: 使用単位)
Successfully migrated X ingredients
```

---

**順番2: 販売価格フィールドの追加**
```bash
python migrate_add_selling_price.py
```

**期待される出力**:
```
============================================================
データベースマイグレーション: selling_price追加
============================================================
データベース: postgresql://...
selling_priceカラムを追加しています...
[OK] selling_priceカラムを正常に追加しました。

新しいフィールド:
  - selling_price: 手動設定の販売価格（NULL=推奨価格を使用）
[OK] マイグレーションが正常に完了しました。
```

---

**順番3: 商品ごとの利益率フィールドの追加**
```bash
python migrate_add_custom_profit_margin.py
```

**期待される出力**:
```
============================================================
データベースマイグレーション: custom_profit_margin追加
============================================================
データベース接続: postgresql://...
custom_profit_marginカラムを追加しています...
[OK] マイグレーション完了: custom_profit_marginカラムを追加しました。
  既存のレシピは基本設定の利益率を使用します（custom_profit_margin = NULL）

[OK] マイグレーションが正常に完了しました。
```

---

### ステップ3: アプリケーションの動作確認

マイグレーション完了後、以下を確認：

#### 3.1 トップページへのアクセス
```
https://bakery-cost-calculator.onrender.com
```

**確認項目**:
- [ ] Internal Server Errorが表示されない
- [ ] ログイン画面が正常に表示される
- [ ] 「ログインIDを忘れた方」リンクが表示される（新機能）

#### 3.2 ログイン後の確認

**材料管理**:
- [ ] 材料一覧が表示される
- [ ] 材料の新規作成画面で「購入単位」と「使用単位」が表示される
- [ ] 既存の材料が正常に表示される

**レシピ管理**:
- [ ] レシピ一覧が表示される
- [ ] レシピの作成・編集画面で以下のフィールドが表示される:
  - [ ] 商品ごとの利益率(%)
  - [ ] 販売価格（円）
- [ ] レシピ詳細で原価と販売価格が表示される

**ラベル印刷**:
- [ ] ラベルプレビュー画面が表示される
- [ ] ラベルサイズ選択ドロップダウンが表示される（7種類のA-ONE製品）
- [ ] カスタムサイズ入力フィールドが表示される

---

## 新機能の確認

### 1. 材料の購入単位と使用単位の分離

**テストシナリオ**:
1. 材料作成画面で「小麦粉」を追加
2. 購入単位: kg、使用単位: g を設定
3. 購入価格: 500円、購入数量: 1kg と入力
4. レシピで「100g」使用した場合、原価が正しく計算されるか確認

**期待される動作**:
- 原価 = 500円 × (100g / 1000g) = 50円

### 2. 販売価格の手動設定

**テストシナリオ**:
1. レシピ作成・編集画面で販売価格フィールドに「300円」と入力
2. 保存後、レシピ詳細で販売価格が「300円」と表示されるか確認

**期待される動作**:
- 販売推奨価格ではなく、手動設定した「300円」が表示される

### 3. 商品ごとの利益率

**テストシナリオ**:
1. レシピ作成・編集画面で「商品ごとの利益率」に「50%」と入力
2. 販売価格を空欄にして保存
3. レシピ詳細で販売推奨価格が利益率50%で計算されているか確認

**期待される動作**:
- 原価100円の場合、販売推奨価格が150円と表示される
- 詳細画面に「商品設定」バッジ（青）が表示される

### 4. パスワードリセット機能

**テストシナリオ**:
1. ログイン画面で「パスワードを忘れた方」リンクをクリック
2. ログインIDを入力
3. 新しいパスワードを設定
4. 新しいパスワードでログインできるか確認

### 5. ログインID確認機能

**テストシナリオ**:
1. ログイン画面で「ログインIDを忘れた方」リンクをクリック
2. 店舗名を入力
3. 該当するログインIDが表示されるか確認

### 6. ラベルサイズカスタマイズ

**テストシナリオ**:
1. レシピ詳細画面で「ラベル印刷」をクリック
2. ラベルサイズドロップダウンから「A-ONE 28754」を選択
3. プレビューが正しく表示されるか確認
4. 「カスタムサイズ」を選択し、幅80mm×高さ50mmを入力
5. プレビューがカスタムサイズで表示されるか確認

---

## トラブルシューティング

### エラー1: Internal Server Error

**原因**: マイグレーションが未実行
**解決**: ステップ2のマイグレーションを順番に実行

### エラー2: カラムが存在しない

**エラーメッセージ例**:
```
column ingredients.purchase_price does not exist
```

**原因**: `migrate_ingredients.py` が未実行
**解決**: Renderシェルで `python migrate_ingredients.py` を実行

### エラー3: マイグレーションスクリプトが見つからない

**エラーメッセージ例**:
```
python: can't open file 'migrate_ingredients.py': [Errno 2] No such file or directory
```

**原因**: デプロイが完了していない、またはファイルがリポジトリに含まれていない
**解決**:
1. Renderのデプロイが完了しているか確認
2. GitHubリポジトリにファイルが存在するか確認
3. Renderで再デプロイを実行

### エラー4: マイグレーションが重複実行された

**心配不要**: すべてのマイグレーションスクリプトは冪等性があり、複数回実行しても問題ありません。

**出力例**:
```
[OK] custom_profit_marginカラムは既に存在します。マイグレーション不要です。
```

---

## PostgreSQL データベース構造（マイグレーション後）

### ingredients テーブル
```sql
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    unit_price NUMERIC(10, 2),  -- 旧フィールド（互換性のため残存）
    unit VARCHAR(20),            -- 旧フィールド（互換性のため残存）
    purchase_price NUMERIC(10, 2),    -- 新: 購入価格
    purchase_quantity NUMERIC(10, 3), -- 新: 購入数量
    purchase_unit VARCHAR(20),        -- 新: 購入単位
    usage_unit VARCHAR(20),           -- 新: 使用単位
    supplier VARCHAR(100),
    is_allergen BOOLEAN,
    allergen_type VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### recipes テーブル
```sql
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    production_quantity INTEGER NOT NULL DEFAULT 1,
    production_time INTEGER DEFAULT 0,
    shelf_life_days INTEGER,
    custom_profit_margin NUMERIC(5, 2),  -- 新: 商品ごとの利益率
    selling_price NUMERIC(10, 2),        -- 新: 手動設定の販売価格
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## デプロイ完了後の最終チェック

### チェックリスト

#### システム全体
- [ ] トップページが表示される
- [ ] ログインができる
- [ ] 各機能ページが表示される（500エラーがない）

#### 材料管理
- [ ] 材料一覧が表示される
- [ ] 材料の新規作成ができる
- [ ] 材料の編集ができる
- [ ] 購入単位と使用単位が正しく表示される

#### レシピ管理
- [ ] レシピ一覧が表示される
- [ ] レシピの新規作成ができる
- [ ] レシピの編集ができる
- [ ] 原価計算が正しく動作する
- [ ] 販売価格が正しく表示される
- [ ] 商品ごとの利益率が機能する

#### ラベル印刷
- [ ] ラベルプレビューが表示される
- [ ] ラベルサイズ選択ができる
- [ ] カスタムサイズ入力ができる
- [ ] PDFダウンロードができる

#### 認証機能
- [ ] パスワードリセットができる
- [ ] ログインID確認ができる

---

## 次回デプロイ時の注意事項

### マイグレーションの管理

今後、新しい機能を追加する際は：

1. **マイグレーションスクリプトを作成**
   - `migrate_*.py` の命名規則に従う
   - 冪等性を確保（複数回実行可能）
   - エラーハンドリングを実装

2. **ドキュメントを更新**
   - DEPLOYMENT_CHECKLIST.md に追加
   - マイグレーション手順を明記

3. **デプロイ後に実行**
   - Renderシェルで手動実行
   - 実行結果をログに記録

### 自動マイグレーションの検討

将来的には、起動時に自動的にマイグレーションを実行する仕組みを検討：

```python
# run.py に追加
from app import create_app, db
import subprocess

app = create_app()

# 起動時にマイグレーションを実行
with app.app_context():
    # マイグレーションスクリプトの実行
    subprocess.run(['python', 'migrate_ingredients.py'])
    subprocess.run(['python', 'migrate_add_selling_price.py'])
    subprocess.run(['python', 'migrate_add_custom_profit_margin.py'])
```

---

## まとめ

### 完了すべきタスク

1. ✅ GitHubから最新コードをpull（完了）
2. ⏳ Renderでの自動デプロイ確認（確認待ち）
3. ⏳ Renderシェルで3つのマイグレーション実行（実行待ち）
4. ⏳ 新機能の動作確認（確認待ち）

### 期待される結果

すべての手順が完了すると：
- Internal Server Errorが解消
- 材料の購入単位と使用単位が分離
- 販売価格の手動設定が可能
- 商品ごとの利益率設定が可能
- パスワードリセット機能が利用可能
- ログインID確認機能が利用可能
- ラベルサイズカスタマイズが可能

---

**作成日**: 2025-10-28
**更新日**: 2025-10-28
**作成者**: Claude Code (AI Assistant)
