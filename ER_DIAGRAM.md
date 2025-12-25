# データベースER図

```mermaid
erDiagram
    Store ||--o| CostSetting : "1:1"
    Store ||--o{ Ingredient : "1:N"
    Store ||--o{ Recipe : "1:N"
    Store ||--o{ CustomCostItem : "1:N"
    Recipe ||--o{ RecipeIngredient : "1:N"
    Ingredient ||--o{ RecipeIngredient : "1:N"

    Store {
        int id PK
        string login_id UK "ログインID"
        string password_hash "パスワードハッシュ"
        string store_name "店舗名"
        datetime created_at "作成日時"
    }

    CostSetting {
        int id PK
        int store_id FK,UK "店舗ID"
        decimal profit_margin "利益率(%)"
        datetime created_at "作成日時"
        datetime updated_at "更新日時"
    }

    Ingredient {
        int id PK
        int store_id FK "店舗ID"
        string name "材料名"
        decimal purchase_price "購入価格"
        decimal purchase_quantity "購入数量"
        string purchase_unit "購入単位(kg,L,個)"
        string usage_unit "使用単位(g,ml,個)"
        decimal unit_price "旧単価フィールド(非推奨)"
        string unit "旧単位フィールド(非推奨)"
        string supplier "仕入先"
        boolean is_allergen "アレルゲンフラグ"
        string allergen_type "アレルゲン種類"
        datetime created_at "作成日時"
        datetime updated_at "更新日時"
    }

    Recipe {
        int id PK
        int store_id FK "店舗ID"
        string product_name "商品名"
        string category "商品カテゴリー"
        int production_quantity "製造個数"
        int production_time "製造時間(分)"
        int shelf_life_days "賞味期限(日数)"
        decimal custom_profit_margin "商品ごとの利益率(%)"
        decimal selling_price "手動設定の販売価格"
        datetime created_at "作成日時"
        datetime updated_at "更新日時"
    }

    RecipeIngredient {
        int id PK
        int recipe_id FK "レシピID"
        int ingredient_id FK "材料ID"
        decimal quantity "使用量"
    }

    CustomCostItem {
        int id PK
        int store_id FK "店舗ID"
        string name "項目名"
        string calculation_type "計算方法(fixed/per_unit/per_time)"
        decimal amount "金額"
        boolean is_active "有効/無効"
        string description "説明"
        int display_order "表示順序"
        datetime created_at "作成日時"
        datetime updated_at "更新日時"
    }
```

## テーブル説明

### Store（店舗テーブル）
パン屋さんの店舗情報を管理。各店舗が独立したログインIDとパスワードを持つ。

### CostSetting（原価計算設定テーブル）
店舗ごとの基本利益率を設定。Storeとは1:1の関係。

### Ingredient（材料マスタテーブル）
材料の情報を管理。購入単位と使用単位を別々に管理し、自動で単位変換を行う。

### Recipe（レシピテーブル）
商品（パン等）のレシピ情報を管理。製造個数、時間、利益率、販売価格などを含む。

### RecipeIngredient（レシピ材料中間テーブル）
レシピと材料の多対多の関係を管理。各材料の使用量を記録。

### CustomCostItem（カスタム原価項目テーブル）
人件費、光熱費、包装費など、材料費以外の原価項目を管理。3つの計算方法をサポート：
- **fixed**: レシピ全体に対して固定金額
- **per_unit**: 製造個数あたりの単価
- **per_time**: 製造時間(分)あたりの単価

## リレーション

- **Store** は複数の **Ingredient**, **Recipe**, **CustomCostItem** を持つ
- **Store** は1つの **CostSetting** を持つ
- **Recipe** は複数の **RecipeIngredient** を通じて複数の **Ingredient** と関連
- **Ingredient** は複数の **RecipeIngredient** を通じて複数の **Recipe** と関連
