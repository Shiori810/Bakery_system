# データベースマイグレーションガイド

## 材料テーブルの更新（購入単位・使用単位の追加）

### 概要
材料の購入単位と使用単位を分離して管理できるように、`ingredients`テーブルに新しいフィールドを追加しました。

### 変更内容
- `purchase_price`: 購入価格
- `purchase_quantity`: 購入数量
- `purchase_unit`: 購入単位 (kg, L, 個など)
- `usage_unit`: 使用単位 (g, ml, 個など)

### マイグレーション手順

#### 1. 本番環境でマイグレーションスクリプトを実行

```bash
# アプリケーションのディレクトリに移動
cd /path/to/Bakery_system

# 仮想環境をアクティベート
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# マイグレーションスクリプトを実行
python migrate_ingredients.py
```

#### 2. 実行結果の確認

スクリプトは以下の処理を自動的に実行します：
1. 新しいカラムを`ingredients`テーブルに追加
2. 既存の材料データを新しいフォーマットに移行
   - `unit_price` → `purchase_price`
   - `unit` → `purchase_unit`, `usage_unit`
   - `purchase_quantity` = 1 (デフォルト)

#### 3. 動作確認

マイグレーション後、以下を確認してください：
- 材料一覧ページが正常に表示されること
- 既存の材料が「使用単位あたり単価」列に表示されること
- 新しい材料を登録できること
- レシピの原価計算が正しく動作すること

### トラブルシューティング

#### エラー: "Column already exists"
すでにマイグレーションが実行されています。スクリプトは自動的にスキップします。

#### エラー: Permission denied
データベースへの書き込み権限を確認してください。

#### 既存データが正しく移行されない場合
1. データベースのバックアップを取る
2. マイグレーションスクリプトを再実行する
3. それでも解決しない場合は、手動でSQLを実行：

```sql
-- 新しいカラムを追加
ALTER TABLE ingredients ADD COLUMN purchase_price NUMERIC(10, 2);
ALTER TABLE ingredients ADD COLUMN purchase_quantity NUMERIC(10, 3) DEFAULT 1;
ALTER TABLE ingredients ADD COLUMN purchase_unit VARCHAR(20);
ALTER TABLE ingredients ADD COLUMN usage_unit VARCHAR(20);

-- 既存データを移行
UPDATE ingredients
SET purchase_price = unit_price,
    purchase_quantity = 1,
    purchase_unit = unit,
    usage_unit = unit
WHERE purchase_price IS NULL;
```

### ロールバック

マイグレーション前の状態に戻す必要がある場合：

```sql
ALTER TABLE ingredients DROP COLUMN purchase_price;
ALTER TABLE ingredients DROP COLUMN purchase_quantity;
ALTER TABLE ingredients DROP COLUMN purchase_unit;
ALTER TABLE ingredients DROP COLUMN usage_unit;
```

### 後方互換性

- 旧フィールド (`unit_price`, `unit`) は保持されています
- 新しいフィールドが空の場合、旧フィールドを使用します
- 既存のレシピは引き続き動作します

### 本番環境へのデプロイ

1. **データベースのバックアップを取る**
2. アプリケーションをメンテナンスモードにする
3. 最新のコードをプル
4. マイグレーションスクリプトを実行
5. アプリケーションを再起動
6. 動作確認
7. メンテナンスモードを解除

```bash
# 例: Render.comの場合
# 1. 環境変数でメンテナンスモードを有効化
# 2. デプロイ
git pull origin main
# 3. Renderが自動的に再起動
# 4. マイグレーションはアプリケーション起動時に自動実行される設定を追加することも可能
```
