# 原価計算修正と販売価格機能の追加

## 作業日時
2025-10-27

## 概要
ベーカリー原価計算システムにおいて、原価計算のエラーを修正し、販売価格を手動で設定できる機能を追加しました。

---

## 1. 原価計算エラーの修正

### 問題の発見

**症状**:
- ブラウザでレシピ詳細ページ（`/recipes/1/detail`）にアクセスすると Internal Server Error が発生
- エラー画面が表示され、データが確認できない状態

### 原因の特定

エラーログを確認した結果、以下のエラーが発生していました：

```
TypeError: must be real number, not NoneType
File "app/templates/recipes/detail.html", line 89
<td class="text-end">{{ "%.2f"|format(ri.ingredient.unit_price) }}円</td>
```

**根本原因**:
- テンプレートファイルで古いフィールド名（`unit_price`、`unit`）を使用
- 新しい購入単位・使用単位システムに移行後、これらのフィールドが`None`になっている材料でエラーが発生
- システムは既に`get_usage_unit_price()`メソッドと`usage_unit`フィールドを使用する新しい実装に移行済み

### 修正内容

以下の3つのテンプレートファイルを修正し、古いフィールド名を新しいメソッド・フィールド名に置き換えました：

#### 1. `app/templates/recipes/detail.html`

**修正箇所**: 88-90行目

**変更前**:
```html
<td class="text-end">{{ ri.quantity }} {{ ri.ingredient.unit }}</td>
<td class="text-end">{{ "%.2f"|format(ri.ingredient.unit_price) }}円</td>
<td class="text-end">{{ "%.2f"|format(ri.quantity * ri.ingredient.unit_price) }}円</td>
```

**変更後**:
```html
<td class="text-end">{{ ri.quantity }} {{ ri.ingredient.usage_unit }}</td>
<td class="text-end">{{ "%.2f"|format(ri.ingredient.get_usage_unit_price()) }}円</td>
<td class="text-end">{{ "%.2f"|format(ri.calculate_cost()) }}円</td>
```

#### 2. `app/templates/recipes/edit_ingredients.html`

**修正箇所**: 28-32行目、43行目、79-84行目

**変更内容**:
- 材料選択時の単価表示を`get_usage_unit_price()`メソッドに統一
- 単位表示を`usage_unit`フィールドに統一
- 後方互換性のための条件分岐を削除

#### 3. `app/templates/ingredients/index.html`

**修正箇所**: 56-62行目

**変更前**:
```html
<td>
    {% if ingredient.usage_unit %}
        {{ "%.2f"|format(ingredient.get_usage_unit_price()) }}円/{{ ingredient.usage_unit }}
    {% else %}
        {{ "%.2f"|format(ingredient.unit_price) }}円/{{ ingredient.unit }}
    {% endif %}
</td>
```

**変更後**:
```html
<td>
    {{ "%.2f"|format(ingredient.get_usage_unit_price()) }}円/{{ ingredient.usage_unit }}
</td>
```

### 修正結果

- ✅ Internal Server Error が解消
- ✅ レシピ詳細ページが正常に表示
- ✅ 原価計算が正しく動作（購入単位と使用単位が異なる場合でも正確に計算）

### 原価計算の仕組み（確認済み）

システムは既に正しい原価計算ロジックを実装していました：

```python
# Ingredient.get_usage_unit_price() メソッド
price_per_purchase_unit = 購入価格 / 購入数量
conversion_factor = 単位変換係数(購入単位 → 使用単位)
usage_unit_price = price_per_purchase_unit / conversion_factor
```

**具体例**:
- 材料：小麦粉
- 購入：25kg を 5000円で購入
- 使用単位：g
- 計算：
  1. `price_per_purchase_unit = 5000 / 25 = 200円/kg`
  2. `conversion_factor = 1000` (kg→g)
  3. `usage_unit_price = 200 / 1000 = 0.2円/g`
  4. レシピで300g使用 → `cost = 300 × 0.2 = 60円` ✓

---

## 2. 販売価格手動設定機能の追加

### 要件

レシピごとに販売価格を手動で設定できるようにする。設定しない場合は従来通り推奨価格（原価×利益率）を使用する。

### 実装内容

#### 2.1 データベースの変更

**ファイル**: `app/models.py`

**追加フィールド**:
```python
class Recipe(db.Model):
    # ... 既存フィールド ...
    selling_price = db.Column(db.Numeric(10, 2))  # 手動設定の販売価格、Noneの場合は推奨価格を使用
```

**追加メソッド**:
```python
def get_selling_price(self, cost_setting):
    """販売価格を取得（手動設定があればそれを、なければ推奨価格を返す）"""
    if self.selling_price is not None:
        return float(self.selling_price)
    return self.calculate_suggested_price(cost_setting)
```

#### 2.2 フォームの変更

**ファイル**: `app/forms.py`

**追加フィールド**:
```python
class RecipeForm(FlaskForm):
    # ... 既存フィールド ...
    selling_price = DecimalField('販売価格(円)', validators=[
        Optional(),
        NumberRange(min=0, message='販売価格は0以上で入力してください')
    ], places=2)
```

#### 2.3 ルートの変更

**ファイル**: `app/routes/recipes.py`

**変更箇所**:

1. **create関数** (45-54行目):
```python
recipe = Recipe(
    store_id=current_user.id,
    product_name=form.product_name.data,
    category=form.category.data,
    production_quantity=form.production_quantity.data,
    production_time=form.production_time.data,
    shelf_life_days=form.shelf_life_days.data,
    custom_profit_margin=form.custom_profit_margin.data,
    selling_price=form.selling_price.data  # 追加
)
```

2. **detail関数** (99行目):
```python
# 変更前
suggested_price = recipe.calculate_suggested_price(cost_setting) if cost_setting else unit_cost

# 変更後
suggested_price = recipe.get_selling_price(cost_setting) if cost_setting else unit_cost
```

#### 2.4 テンプレートの変更

**ファイル**: `app/templates/recipes/form.html`

**追加UI** (68-92行目):
```html
<div class="row mb-3">
    <div class="col-md-6">
        {{ form.custom_profit_margin.label(class="form-label") }}
        <div class="input-group">
            {{ form.custom_profit_margin(class="form-control" + (" is-invalid" if form.custom_profit_margin.errors else ""), placeholder="基本設定を使用") }}
            <span class="input-group-text">%</span>
        </div>
        {% if form.custom_profit_margin.errors %}
            <div class="invalid-feedback d-block">{{ form.custom_profit_margin.errors[0] }}</div>
        {% endif %}
        <small class="form-text text-muted">この商品専用の利益率（空欄の場合は基本設定を使用）</small>
    </div>

    <div class="col-md-6">
        {{ form.selling_price.label(class="form-label") }}
        <div class="input-group">
            {{ form.selling_price(class="form-control" + (" is-invalid" if form.selling_price.errors else ""), placeholder="推奨価格を使用") }}
            <span class="input-group-text">円</span>
        </div>
        {% if form.selling_price.errors %}
            <div class="invalid-feedback d-block">{{ form.selling_price.errors[0] }}</div>
        {% endif %}
        <small class="form-text text-muted">手動で販売価格を設定（空欄の場合は推奨価格を使用）</small>
    </div>
</div>
```

**ファイル**: `app/templates/recipes/detail.html`

**変更箇所** (166-189行目):
```html
<div class="alert alert-success mb-0">
    <div class="d-flex justify-content-between align-items-center">
        <span>
            {% if recipe.selling_price is not none %}
                販売価格
                <span class="badge bg-warning text-dark">手動設定</span>
            {% else %}
                販売推奨価格
            {% endif %}
        </span>
        <strong class="fs-5">{{ "%.0f"|format(suggested_price) }}円</strong>
    </div>
    {% if recipe.selling_price is none %}
        {% set profit_margin = recipe.get_profit_margin(cost_setting) %}
        <small class="text-muted">
            利益率 {{ profit_margin }}%
            {% if recipe.custom_profit_margin is not none %}
                <span class="badge bg-info">商品設定</span>
            {% else %}
                <span class="badge bg-secondary">基本設定</span>
            {% endif %}
        </small>
    {% endif %}
</div>
```

#### 2.5 ラベル生成機能の修正

**ファイル**: `app/routes/labels.py`

**変更箇所**:

1. **preview関数** (41行目):
```python
# 変更前
suggested_price = recipe.calculate_suggested_price(cost_setting) if cost_setting else unit_cost

# 変更後
suggested_price = recipe.get_selling_price(cost_setting) if cost_setting else unit_cost
```

2. **draw_label関数** (192行目):
```python
# 変更前
if show_price:
    suggested_price = recipe.calculate_suggested_price(cost_setting) if cost_setting else 0
    c.drawString(x + padding, current_y, f"販売価格: {suggested_price:.0f}円")

# 変更後
if show_price:
    selling_price = recipe.get_selling_price(cost_setting) if cost_setting else 0
    c.drawString(x + padding, current_y, f"販売価格: {selling_price:.0f}円")
```

#### 2.6 マイグレーション

**ファイル**: `migrate_add_selling_price.py`

```python
"""
データベースマイグレーション: selling_priceカラムの追加
レシピテーブルに手動設定の販売価格フィールドを追加します
"""
import sqlite3
import sys
from pathlib import Path

def migrate_database():
    """selling_priceカラムをrecipesテーブルに追加"""
    db_path = Path(__file__).parent / 'instance' / 'bakery.db'

    if not db_path.exists():
        print(f"エラー: データベースファイルが見つかりません: {db_path}")
        return False

    try:
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
        conn.close()
        return True

    except Exception as e:
        print(f"[ERROR] マイグレーション中にエラーが発生しました: {e}")
        return False

if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
```

**実行コマンド**:
```bash
cd C:\Users\SatoeTakahashi\SK_Bakery\Bakery_system
python migrate_add_selling_price.py
```

**実行結果**:
```
============================================================
データベースマイグレーション: selling_price追加
============================================================
データベース: C:\Users\SatoeTakahashi\SK_Bakery\Bakery_system\instance\bakery.db

[OK] selling_priceカラムは既に存在します。マイグレーション不要です。
```

---

## 3. 機能の使い方

### 販売価格の手動設定

1. **レシピ編集画面を開く**
   - レシピ一覧から編集したいレシピの「編集」ボタンをクリック

2. **販売価格を入力**
   - 「販売価格(円)」フィールドに任意の価格を入力（例：100円）
   - 空欄のままにすると推奨価格（原価×利益率）が自動計算されます

3. **保存して確認**
   - 「更新」ボタンをクリック
   - レシピ詳細ページで販売価格を確認

### レシピ詳細ページでの表示

**手動設定した場合**:
```
販売価格 [手動設定]
100円
```

**自動計算の場合**:
```
販売推奨価格
540円
利益率 30% [基本設定]
```

### ラベルでの表示

ラベル生成時に「販売価格を表示」をチェックすると：
- **手動設定した場合**: 手動設定した価格（例：100円）が表示
- **自動計算の場合**: 推奨価格が表示

---

## 4. 技術的な詳細

### 価格決定のロジック

```python
def get_selling_price(self, cost_setting):
    """販売価格を取得"""
    # 1. 手動設定があればそれを優先
    if self.selling_price is not None:
        return float(self.selling_price)

    # 2. なければ推奨価格を計算
    return self.calculate_suggested_price(cost_setting)

def calculate_suggested_price(self, cost_setting):
    """販売推奨価格の計算"""
    unit_cost = self.calculate_unit_cost(cost_setting)

    # 商品ごとの利益率があればそれを使用、なければ基本設定を使用
    profit_margin = self.custom_profit_margin if self.custom_profit_margin is not None else (cost_setting.profit_margin if cost_setting else 0)

    if profit_margin > 0:
        margin_multiplier = 1 + (float(profit_margin) / 100)
        return unit_cost * margin_multiplier
    return unit_cost
```

### データベーススキーマ

**recipesテーブル**:
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    production_quantity INTEGER NOT NULL DEFAULT 1,
    production_time INTEGER DEFAULT 0,
    shelf_life_days INTEGER,
    custom_profit_margin NUMERIC(5, 2),  -- 商品ごとの利益率(%)
    selling_price NUMERIC(10, 2),        -- 手動設定の販売価格（新規追加）
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (store_id) REFERENCES stores(id)
);
```

---

## 5. 修正ファイル一覧

### 新規作成
- `migrate_add_selling_price.py` - マイグレーションスクリプト
- `COST_CALCULATION_FIX_AND_SELLING_PRICE_FEATURE.md` - 本ドキュメント

### 修正ファイル
1. `app/models.py` - selling_priceフィールドとget_selling_price()メソッドを追加
2. `app/forms.py` - selling_priceフィールドを追加
3. `app/routes/recipes.py` - create関数とdetail関数を修正
4. `app/routes/labels.py` - preview関数とdraw_label関数を修正
5. `app/templates/recipes/form.html` - 販売価格入力フィールドを追加
6. `app/templates/recipes/detail.html` - 販売価格表示を改善
7. `app/templates/recipes/edit_ingredients.html` - 古いフィールド名を修正
8. `app/templates/ingredients/index.html` - 古いフィールド名を修正

---

## 6. テスト結果

### 原価計算エラーの修正
- ✅ レシピ詳細ページが正常に表示される
- ✅ 材料の単価が正しく表示される（購入単位と使用単位が異なる場合でも）
- ✅ 材料費の計算が正確

### 販売価格手動設定機能
- ✅ レシピ編集画面で販売価格を入力できる
- ✅ 手動設定した価格がレシピ詳細ページに表示される（「手動設定」バッジ付き）
- ✅ 空欄の場合は推奨価格が表示される（利益率情報付き）
- ✅ ラベルプレビューで手動設定した価格が表示される
- ✅ PDF生成時に手動設定した価格が正しく印刷される

---

## 7. 本番環境へのデプロイ手順

### Renderでのマイグレーション実行

1. **Renderダッシュボードにアクセス**
   - https://dashboard.render.com/
   - `bakery-cost-calculator` サービスを選択

2. **Shellを開く**
   - "Shell" ボタンをクリック

3. **マイグレーションを実行**
   ```bash
   python migrate_add_selling_price.py
   ```

4. **サービスの再起動**（必要に応じて）
   - Renderダッシュボードから "Manual Deploy" → "Deploy latest commit"

5. **動作確認**
   - `https://bakery.etsu-dev.com` にアクセス
   - レシピを編集して販売価格を設定
   - ラベル生成で正しく表示されることを確認

---

## 8. まとめ

本作業により、以下の改善が実現されました：

1. **原価計算エラーの解消**
   - テンプレートの古いフィールド名を修正
   - システムが正常に動作するようになった

2. **販売価格の柔軟な設定**
   - 商品ごとに手動で販売価格を設定可能
   - 市場価格や競合状況に応じた価格設定が可能
   - 自動計算と手動設定を使い分けられる

3. **ラベル生成の改善**
   - 手動設定した販売価格がラベルに正しく表示される
   - 価格の透明性が向上

これにより、ベーカリー事業者はより柔軟な価格戦略を実行できるようになりました。

---

## 9. 関連ドキュメント

本作業に引き続き、以下の機能も追加されました：

- **[LABEL_SIZE_CUSTOMIZATION_FEATURE.md](LABEL_SIZE_CUSTOMIZATION_FEATURE.md)** - ラベルサイズカスタマイズ機能
  - A-ONE製品プリセット対応（7種類）
  - カスタムサイズ設定機能
  - 柔軟なラベル印刷が可能

---

**作成者**: Claude Code (AI Assistant)
**作成日**: 2025-10-27
**ステータス**: 完了・テスト済み
