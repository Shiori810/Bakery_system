# 人件費・光熱費のカスタム原価項目化 実装計画書

## 概要

人件費と光熱費をCostSettingテーブルの専用フィールドから、CustomCostItem管理システムへ移行する。

**目的**:
- すべての原価項目を統一的なシステムで管理
- より柔軟な原価設定を可能にする
- コードの簡素化と保守性向上

---

## 現状分析

### 1. 現在の実装 (CostSetting)

**データモデル** ([app/models.py:37-52](app/models.py#L37-L52)):
```python
class CostSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False, unique=True)
    include_labor_cost = db.Column(db.Boolean, default=False)
    include_utility_cost = db.Column(db.Boolean, default=False)
    hourly_wage = db.Column(db.Numeric(10, 2), default=0.0)  # 時給
    monthly_utility_cost = db.Column(db.Numeric(10, 2), default=0.0)  # 月額光熱費
    profit_margin = db.Column(db.Numeric(5, 2), default=30.0)  # 利益率(%)
```

**計算ロジック** ([app/models.py:189-216](app/models.py#L189-L216)):
```python
# 人件費の計算
if cost_setting.include_labor_cost and self.production_time > 0:
    labor_cost = float(cost_setting.hourly_wage) * (self.production_time / 60)
    total_cost += labor_cost

# 光熱費の計算(月額を30日で割って時間按分)
if cost_setting.include_utility_cost and self.production_time > 0:
    daily_utility = float(cost_setting.monthly_utility_cost) / 30
    hourly_utility = daily_utility / 24
    utility_cost = hourly_utility * (self.production_time / 60)
    total_cost += utility_cost
```

**計算式まとめ**:
- **人件費**: `hourly_wage × (production_time / 60)` 円
- **光熱費**: `(monthly_utility_cost / 30 / 24) × (production_time / 60)` 円

---

### 2. CustomCostItem システム

**データモデル** ([app/models.py:277-322](app/models.py#L277-L322)):
```python
class CustomCostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 項目名
    calculation_type = db.Column(db.String(20), nullable=False)  # 'fixed', 'per_unit', 'per_time'
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
```

**計算タイプ**:
- `fixed`: レシピ全体に対して固定額
- `per_unit`: 製造個数 × 単価
- `per_time`: 製造時間(分) × 分単価

**計算ロジック** ([app/models.py:292-319](app/models.py#L292-L319)):
```python
def calculate_cost(self, recipe):
    if not self.is_active:
        return 0.0

    if self.calculation_type == 'fixed':
        return float(self.amount)
    elif self.calculation_type == 'per_unit':
        return float(self.amount) * recipe.production_quantity
    elif self.calculation_type == 'per_time':
        if recipe.production_time > 0:
            return float(self.amount) * recipe.production_time
        return 0.0
```

---

## 移行戦略

### マッピング方針

| 現在のフィールド | CustomCostItem への変換 |
|---------------|----------------------|
| `hourly_wage` (時給) | `calculation_type='per_time'`, `amount=hourly_wage/60` (分単価に変換) |
| `monthly_utility_cost` (月額光熱費) | `calculation_type='per_time'`, `amount=monthly_utility_cost/30/24/60` (分単価に変換) |
| `include_labor_cost` (フラグ) | `is_active` (有効/無効) |
| `include_utility_cost` (フラグ) | `is_active` (有効/無効) |

### 計算式の変換

#### 人件費
- **現在**: `hourly_wage × (production_time / 60)`
- **移行後**: `(hourly_wage / 60) × production_time`
- **amount値**: `hourly_wage / 60` (分単価)

**例**: 時給1,200円の場合
- 現在: `1200 × (180 / 60) = 3600円`
- 移行後: `(1200 / 60) × 180 = 20 × 180 = 3600円` ✓同じ結果

#### 光熱費
- **現在**: `(monthly_utility_cost / 30 / 24) × (production_time / 60)`
- **移行後**: `(monthly_utility_cost / 30 / 24 / 60) × production_time`
- **amount値**: `monthly_utility_cost / 43200` (分単価)

**例**: 月額30,000円の場合
- 現在: `(30000 / 30 / 24) × (180 / 60) = 41.67 × 3 = 125円`
- 移行後: `(30000 / 43200) × 180 = 0.694 × 180 = 125円` ✓同じ結果

---

## 実装手順

### ステップ1: データベースマイグレーション

**ファイル名**: `migrate_labor_utility_to_custom_costs.py`

**処理内容**:
1. 全店舗のCostSettingレコードを取得
2. 各店舗について:
   - `hourly_wage > 0` の場合:
     - CustomCostItem「人件費」を作成
     - `calculation_type = 'per_time'`
     - `amount = hourly_wage / 60` (分単価に変換)
     - `is_active = include_labor_cost` (フラグを引き継ぐ)
     - `description = '時給: {hourly_wage}円から自動生成'`

   - `monthly_utility_cost > 0` の場合:
     - CustomCostItem「光熱費」を作成
     - `calculation_type = 'per_time'`
     - `amount = monthly_utility_cost / 43200` (分単価に変換)
     - `is_active = include_utility_cost` (フラグを引き継ぐ)
     - `description = '月額: {monthly_utility_cost}円から自動生成'`

3. CostSettingテーブルから以下のカラムを削除:
   - `include_labor_cost`
   - `include_utility_cost`
   - `hourly_wage`
   - `monthly_utility_cost`

**注意事項**:
- 既に「人件費」「光熱費」という名前のCustomCostItemが存在する場合はスキップ
- マイグレーション前にバックアップを推奨
- 冪等性を確保（複数回実行可能）

---

### ステップ2: モデルとロジックの更新

#### 2.1 CostSetting モデルの更新 ([app/models.py:37-52](app/models.py#L37-L52))

**削除するフィールド**:
```python
# 削除
include_labor_cost = db.Column(db.Boolean, default=False)
include_utility_cost = db.Column(db.Boolean, default=False)
hourly_wage = db.Column(db.Numeric(10, 2), default=0.0)
monthly_utility_cost = db.Column(db.Numeric(10, 2), default=0.0)
```

**残すフィールド**:
```python
# 残す
id = db.Column(db.Integer, primary_key=True)
store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False, unique=True)
profit_margin = db.Column(db.Numeric(5, 2), default=30.0)
```

#### 2.2 Recipe.calculate_total_cost() の更新 ([app/models.py:189-216](app/models.py#L189-L216))

**削除するコード**:
```python
# 人件費の追加 - 削除
if cost_setting.include_labor_cost and self.production_time > 0:
    labor_cost = float(cost_setting.hourly_wage) * (self.production_time / 60)
    total_cost += labor_cost

# 光熱費の追加 - 削除
if cost_setting.include_utility_cost and self.production_time > 0:
    daily_utility = float(cost_setting.monthly_utility_cost) / 30
    hourly_utility = daily_utility / 24
    utility_cost = hourly_utility * (self.production_time / 60)
    total_cost += utility_cost
```

**既存のCustomCostItemループがすべてを処理**:
```python
# カスタム原価項目の追加（人件費・光熱費も含む）
custom_items = CustomCostItem.query.filter_by(
    store_id=self.store_id,
    is_active=True
).all()

for item in custom_items:
    total_cost += item.calculate_cost(self)
```

---

### ステップ3: フォームとUIの更新

#### 3.1 CostSettingForm の更新 ([app/forms.py](app/forms.py))

**削除するフィールド**:
```python
# 削除
include_labor_cost = BooleanField('人件費を含める')
include_utility_cost = BooleanField('光熱費を含める')
hourly_wage = DecimalField('時給', ...)
monthly_utility_cost = DecimalField('月額光熱費', ...)
```

**残すフィールド**:
```python
# 残す
profit_margin = DecimalField('利益率(%)', ...)
```

#### 3.2 設定画面テンプレートの更新 ([app/templates/main/settings.html](app/templates/main/settings.html))

**削除する要素** (lines 16-61):
- チェックボックス (include_labor_cost, include_utility_cost)
- 時給入力フィールド (hourly_wage)
- 月額光熱費入力フィールド (monthly_utility_cost)

**強調する要素**:
- カスタム原価項目管理へのリンクを目立たせる
- 「人件費と光熱費はカスタム原価項目で管理します」という説明を追加

**新しい構成案**:
```html
<div class="alert alert-primary mb-4">
    <h5><i class="bi bi-calculator-fill"></i> 原価項目の管理</h5>
    <p class="mb-2">
        人件費、光熱費、包装費、減価償却費など、すべての原価項目は
        <strong>カスタム原価項目管理</strong>で設定します。
    </p>
    <a href="{{ url_for('custom_costs.index') }}" class="btn btn-primary">
        <i class="bi bi-calculator-fill"></i> カスタム原価項目管理を開く
    </a>
</div>

<div class="mb-4">
    <h5>利益率設定</h5>
    {{ form.profit_margin.label(class="form-label") }}
    <div class="input-group" style="max-width: 300px;">
        {{ form.profit_margin(class="form-control") }}
        <span class="input-group-text">%</span>
    </div>
    <small class="form-text text-muted">販売推奨価格の計算に使用されます</small>
</div>
```

#### 3.3 説明カードの更新 ([app/templates/main/settings.html:88-106](app/templates/main/settings.html#L88-L106))

**変更前**:
- 人件費の説明
- 光熱費の説明
- 利益率の説明

**変更後**:
```html
<div class="card bg-light">
    <div class="card-body">
        <h5 class="card-title"><i class="bi bi-info-circle"></i> 設定について</h5>

        <p class="card-text">
            <strong>利益率</strong><br>
            原価に利益率を上乗せして販売推奨価格を計算します。<br>
            商品ごとに個別の利益率を設定することもできます。
        </p>

        <hr>

        <p class="card-text">
            <strong>原価項目の管理</strong><br>
            人件費、光熱費、その他すべての原価項目は
            <a href="{{ url_for('custom_costs.index') }}">カスタム原価項目管理</a>
            で設定します。
        </p>

        <ul class="small">
            <li><strong>人件費</strong>: 時間あたり(分単位)で設定</li>
            <li><strong>光熱費</strong>: 時間あたり(分単位)で設定</li>
            <li><strong>その他</strong>: 固定費、個数あたりなど柔軟に設定可能</li>
        </ul>
    </div>
</div>
```

---

### ステップ4: カスタム原価項目管理UIの改善

#### 4.1 説明文の更新 ([app/templates/custom_costs/index.html:9-14](app/templates/custom_costs/index.html#L9-L14))

**変更前**:
```html
<div class="alert alert-info">
    <strong>カスタム原価項目とは？</strong><br>
    材料費・人件費・光熱費以外の原価を自由に設定できます。<br>
    例: 包装費、減価償却費、配送費、家賃按分など
</div>
```

**変更後**:
```html
<div class="alert alert-info">
    <strong>カスタム原価項目とは？</strong><br>
    材料費以外のすべての原価項目を自由に設定できます。<br>
    <strong>例</strong>: 人件費、光熱費、包装費、減価償却費、配送費、家賃按分など
</div>
```

#### 4.2 ヘルプテキストの更新 ([app/templates/custom_costs/index.html:137-147](app/templates/custom_costs/index.html#L137-L147))

**追加情報**:
```html
<div class="alert alert-light mt-3">
    <small>
        <i class="bi bi-lightbulb"></i>
        <strong>ヒント:</strong>
        <ul class="mb-0 mt-2">
            <li><strong>固定費</strong>: レシピ全体に対して一定額を加算（例: 包装材料費50円）</li>
            <li><strong>個数あたり</strong>: 製造個数 × 単価で計算（例: 袋代10円/個 × 10個 = 100円）</li>
            <li><strong>時間あたり</strong>: 製造時間(分) × 分単価で計算（例: 人件費20円/分 × 180分 = 3600円）</li>
        </ul>

        <hr class="my-2">

        <strong>時給から分単価への換算例:</strong>
        <ul class="mb-0 mt-2">
            <li>時給1,200円 → 分単価20円 (1200 ÷ 60)</li>
            <li>時給1,500円 → 分単価25円 (1500 ÷ 60)</li>
        </ul>

        <strong>月額光熱費から分単価への換算例:</strong>
        <ul class="mb-0 mt-2">
            <li>月額30,000円 → 分単価0.69円 (30000 ÷ 30日 ÷ 24時間 ÷ 60分)</li>
            <li>月額45,000円 → 分単価1.04円 (45000 ÷ 43200)</li>
        </ul>
    </small>
</div>
```

---

### ステップ5: マイグレーションツールの作成

#### 5.1 時給・月額光熱費から分単価への変換ヘルパー

ユーザーが既存の設定値から簡単に分単価を計算できるように、Webベースの変換ツールをカスタム原価項目管理画面に追加:

```html
<!-- 変換ヘルパー -->
<div class="card mb-4 bg-light">
    <div class="card-header">
        <h5 class="mb-0"><i class="bi bi-calculator"></i> 分単価変換ツール</h5>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-6">
                <h6>時給 → 分単価</h6>
                <div class="input-group mb-2">
                    <span class="input-group-text">時給</span>
                    <input type="number" id="hourly_wage_input" class="form-control" placeholder="1200">
                    <span class="input-group-text">円</span>
                </div>
                <div class="alert alert-success mb-0">
                    分単価: <strong id="per_minute_labor">-</strong> 円/分
                </div>
            </div>

            <div class="col-md-6">
                <h6>月額光熱費 → 分単価</h6>
                <div class="input-group mb-2">
                    <span class="input-group-text">月額</span>
                    <input type="number" id="monthly_utility_input" class="form-control" placeholder="30000">
                    <span class="input-group-text">円</span>
                </div>
                <div class="alert alert-success mb-0">
                    分単価: <strong id="per_minute_utility">-</strong> 円/分
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('hourly_wage_input').addEventListener('input', function() {
    const hourlyWage = parseFloat(this.value) || 0;
    const perMinute = (hourlyWage / 60).toFixed(2);
    document.getElementById('per_minute_labor').textContent = perMinute;
});

document.getElementById('monthly_utility_input').addEventListener('input', function() {
    const monthlyUtility = parseFloat(this.value) || 0;
    const perMinute = (monthlyUtility / 43200).toFixed(4);
    document.getElementById('per_minute_utility').textContent = perMinute;
});
</script>
```

---

## テスト計画

### 1. マイグレーション前後の計算結果比較

**テストケース**:

| 項目 | 設定値 | レシピ条件 | 期待される原価 |
|-----|-------|-----------|------------|
| 人件費 | 時給1,200円 | 製造時間180分 | 3,600円 |
| 光熱費 | 月額30,000円 | 製造時間180分 | 125円 |
| 両方 | 上記 | 製造時間180分 | 3,725円 |
| 人件費無効 | 時給1,200円、無効 | 製造時間180分 | 0円 |

**検証方法**:
1. マイグレーション前に原価を記録
2. マイグレーション実行
3. 同じレシピで原価を再計算
4. 結果が一致することを確認

### 2. エッジケースのテスト

- 人件費のみ設定されている店舗
- 光熱費のみ設定されている店舗
- 両方とも0円の店舗
- 両方とも無効(include_xxx_cost = False)の店舗
- 製造時間が0分のレシピ
- 既に「人件費」「光熱費」という名前のCustomCostItemが存在する店舗

### 3. UI/UX テスト

- 設定画面から人件費・光熱費フィールドが削除されている
- カスタム原価項目管理画面で人件費・光熱費が正しく表示される
- 有効/無効の切り替えが正しく動作する
- レシピ詳細画面で原価内訳が正しく表示される

---

## ロールバック計画

万が一問題が発生した場合の復旧手順:

### データベースレベルのロールバック

1. **カラムの復元**:
   ```sql
   ALTER TABLE cost_settings ADD COLUMN include_labor_cost BOOLEAN DEFAULT FALSE;
   ALTER TABLE cost_settings ADD COLUMN include_utility_cost BOOLEAN DEFAULT FALSE;
   ALTER TABLE cost_settings ADD COLUMN hourly_wage NUMERIC(10, 2) DEFAULT 0.0;
   ALTER TABLE cost_settings ADD COLUMN monthly_utility_cost NUMERIC(10, 2) DEFAULT 0.0;
   ```

2. **CustomCostItemから値を復元**:
   ```python
   # 「人件費」CustomCostItemから hourly_wage を復元
   labor_item = CustomCostItem.query.filter_by(
       store_id=store_id,
       name='人件費'
   ).first()

   if labor_item:
       cost_setting.hourly_wage = labor_item.amount * 60  # 分単価 → 時給
       cost_setting.include_labor_cost = labor_item.is_active

   # 「光熱費」CustomCostItemから monthly_utility_cost を復元
   utility_item = CustomCostItem.query.filter_by(
       store_id=store_id,
       name='光熱費'
   ).first()

   if utility_item:
       cost_setting.monthly_utility_cost = utility_item.amount * 43200  # 分単価 → 月額
       cost_setting.include_utility_cost = utility_item.is_active
   ```

3. **コードのロールバック**:
   - Gitで前のコミットに戻す
   - `git revert <commit-hash>`

---

## デプロイ手順

### 開発環境でのテスト

1. ローカルでマイグレーションスクリプトを作成
2. テストデータで動作確認
3. 計算結果が一致することを確認
4. UIの表示を確認

### 本番環境へのデプロイ

1. **コードのデプロイ**:
   ```bash
   git add .
   git commit -m "Refactor: 人件費・光熱費をCustomCostItem管理に移行"
   git push origin main
   ```

2. **Renderでの自動デプロイ待機**

3. **Renderシェルでマイグレーション実行**:
   ```bash
   python migrate_labor_utility_to_custom_costs.py
   ```

4. **動作確認**:
   - 設定画面の表示確認
   - カスタム原価項目管理画面の確認
   - レシピ詳細画面で原価計算が正しいか確認

5. **ドキュメント更新**:
   - README.md の更新
   - 機能ドキュメントの作成
   - デプロイチェックリストの更新

---

## リスク分析

### 高リスク

| リスク | 影響 | 対策 |
|-------|-----|-----|
| マイグレーション失敗 | 原価計算が不正確になる | 冪等性を確保、テストの徹底 |
| データ損失 | 既存の設定値が失われる | バックアップ必須、ロールバック手順準備 |

### 中リスク

| リスク | 影響 | 対策 |
|-------|-----|-----|
| UI混乱 | ユーザーが設定方法がわからない | 詳細な説明と変換ツールを提供 |
| 計算精度 | 小数点以下の誤差 | Decimalを使用、テストで検証 |

### 低リスク

| リスク | 影響 | 対策 |
|-------|-----|-----|
| 重複項目作成 | 「人件費」が複数できる | マイグレーションで存在チェック |

---

## メリット・デメリット

### メリット

1. **統一的な管理**: すべての原価項目を一つのシステムで管理
2. **柔軟性の向上**: 人件費・光熱費も他の原価項目と同様に柔軟に設定可能
3. **コードの簡素化**: 特殊な計算ロジックを削減
4. **拡張性**: 将来的な原価項目の追加が容易
5. **UI/UXの改善**: 一つの画面ですべての原価項目を管理

### デメリット

1. **ユーザーの学習コスト**: 既存ユーザーが新しい管理方法を学ぶ必要がある
2. **入力の複雑さ**: 時給を分単価に変換する手間
3. **マイグレーションの複雑さ**: 慎重な実装とテストが必要

### デメリットの緩和策

1. **変換ツールの提供**: 時給・月額から分単価への自動変換
2. **詳細なヘルプ**: 画面上に計算例と説明を表示
3. **段階的な移行**: まず開発環境で十分にテスト

---

## タイムライン

| ステップ | 作業内容 | 所要時間 |
|---------|---------|---------|
| 1 | マイグレーションスクリプト作成 | 1時間 |
| 2 | モデル・ロジックの更新 | 1時間 |
| 3 | フォーム・UIの更新 | 2時間 |
| 4 | 変換ツールの実装 | 1時間 |
| 5 | テスト（ローカル） | 1時間 |
| 6 | ドキュメント作成 | 1時間 |
| 7 | 本番デプロイ | 30分 |
| **合計** | | **約7.5時間** |

---

## 実装チェックリスト

### コード変更

- [ ] マイグレーションスクリプト作成 (`migrate_labor_utility_to_custom_costs.py`)
- [ ] CostSettingモデルの更新 (フィールド削除)
- [ ] Recipe.calculate_total_cost()の更新 (ロジック削除)
- [ ] CostSettingFormの更新 (フィールド削除)
- [ ] settings.htmlテンプレートの更新
- [ ] custom_costs/index.htmlテンプレートの更新 (説明文改善)
- [ ] 変換ツールの実装 (custom_costs/index.html)

### テスト

- [ ] マイグレーション前後の計算結果比較
- [ ] エッジケースのテスト
- [ ] UI/UXテスト
- [ ] ブラウザ互換性テスト

### ドキュメント

- [ ] 実装計画書 (このファイル)
- [ ] 機能説明ドキュメント
- [ ] README.mdの更新
- [ ] DEPLOYMENT_CHECKLIST.mdの更新
- [ ] ユーザーガイド (必要に応じて)

### デプロイ

- [ ] 開発環境でのテスト完了
- [ ] コードのコミット・プッシュ
- [ ] Renderでの自動デプロイ確認
- [ ] Renderシェルでマイグレーション実行
- [ ] 本番環境での動作確認

---

## 関連ファイル

- [app/models.py](app/models.py) - CostSetting, Recipe, CustomCostItem モデル
- [app/forms.py](app/forms.py) - CostSettingForm
- [app/routes/custom_costs.py](app/routes/custom_costs.py) - カスタム原価項目管理ルート
- [app/templates/main/settings.html](app/templates/main/settings.html) - 設定画面
- [app/templates/custom_costs/index.html](app/templates/custom_costs/index.html) - カスタム原価項目管理画面
- [migrate_labor_utility_to_custom_costs.py](migrate_labor_utility_to_custom_costs.py) - マイグレーションスクリプト (作成予定)

---

## まとめ

この移行により、パン屋向け原価計算アプリケーションは、より統一的で柔軟な原価管理システムを持つことになります。

**主な変更点**:
1. 人件費・光熱費が専用フィールドからCustomCostItemへ移行
2. 設定画面がシンプルになり、カスタム原価項目管理に一本化
3. すべての原価項目を同じUIで管理可能

**ユーザーへの影響**:
- 既存の設定は自動的に変換されるため、原価計算結果は変わらない
- 設定方法が変更されるため、変換ツールとヘルプで対応

**技術的な改善**:
- コードの簡素化と保守性向上
- 将来的な拡張が容易
- 一貫性のあるデータモデル

---

**作成日**: 2025-10-29
**作成者**: Claude Code (AI Assistant)
**バージョン**: 1.0
