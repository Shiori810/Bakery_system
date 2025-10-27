# ラベルサイズカスタマイズ機能の追加

## 作業日時
2025-10-27

## 概要
ベーカリー原価計算システムのラベル印刷機能に、A-ONE製品プリセットとカスタムサイズ設定機能を追加しました。これにより、市販のラベル用紙に対応し、柔軟なラベル印刷が可能になりました。

---

## 1. 背景と要件

### 要望
- ラベルサイズを縦横自由に設定できるようにしたい
- A-ONE製品のラベル用紙に印刷できるようにしたい
- よく使う商品にすぐに対応できるようにしたい

### 課題
従来のシステムでは、ラベルサイズが固定（90mm × 60mm）で、A4用紙に8面（2列 × 4行）のみの対応でした。市販のラベル用紙には様々なサイズがあり、柔軟な対応が必要でした。

---

## 2. 実装内容

### 2.1 A-ONE製品プリセットの追加

A-ONEの主要なラベル製品7種類に対応しました：

| 品番 | 面数 | サイズ (mm) | 列×行 | 用途 |
|------|------|-------------|-------|------|
| 31531 | 12面 | 86.4 × 42.3 | 2×6 | 宛名ラベル |
| 72210 | 10面 | 86.4 × 50.8 | 2×5 | 宛名ラベル（大） |
| 31538 | 21面 | 70.0 × 42.3 | 3×7 | 宛名ラベル（小） |
| 28918 | 8面 | 99.0 × 67.5 | 2×4 | 表示ラベル |
| 28729 | 18面 | 63.5 × 46.6 | 3×6 | 表示ラベル（中） |
| 28315 | 24面 | 66.0 × 33.9 | 3×8 | 表示ラベル（小） |
| 28765 | 65面 | 38.1 × 21.2 | 5×13 | インデックスラベル |

### 2.2 カスタムサイズ設定

以下のパラメータを自由に設定可能：

- **ラベルサイズ**
  - 幅（mm）：10mm以上、0.1mm単位
  - 高さ（mm）：10mm以上、0.1mm単位

- **レイアウト**
  - 列数：1〜10列
  - 行数：1〜20行

- **余白・間隔**
  - 左余白（mm）：0mm以上、0.1mm単位
  - 上余白（mm）：0mm以上、0.1mm単位
  - 横間隔（mm）：0mm以上、0.1mm単位
  - 縦間隔（mm）：0mm以上、0.1mm単位

---

## 3. 技術的な実装

### 3.1 プリセットデータ構造

**ファイル**: `app/routes/labels.py`

```python
LABEL_PRESETS = {
    'custom': {
        'name': 'カスタムサイズ',
        'width': 90,
        'height': 60,
        'cols': 2,
        'rows': 4,
        'margin_left': 15,
        'margin_top': 20,
        'gap_x': 10,
        'gap_y': 8
    },
    '31531': {
        'name': 'A-ONE 31531 (12面)',
        'product_code': '31531',
        'width': 86.4,
        'height': 42.3,
        'cols': 2,
        'rows': 6,
        'margin_left': 11.5,
        'margin_top': 21.0,
        'gap_x': 5.1,
        'gap_y': 0
    },
    # ... 他のプリセット
}
```

### 3.2 ラベル生成ロジックの修正

**ファイル**: `app/routes/labels.py` (157-187行目)

```python
# ラベルサイズ設定の取得
label_preset = request.form.get('label_preset', 'custom')

# プリセットまたはカスタムサイズの取得
if label_preset == 'custom':
    # カスタムサイズ
    label_width = float(request.form.get('custom_width', 90)) * mm
    label_height = float(request.form.get('custom_height', 60)) * mm
    cols = int(request.form.get('custom_cols', 2))
    rows = int(request.form.get('custom_rows', 4))
    margin_left = float(request.form.get('custom_margin_left', 15)) * mm
    margin_top = float(request.form.get('custom_margin_top', 20)) * mm
    gap_x = float(request.form.get('custom_gap_x', 10)) * mm
    gap_y = float(request.form.get('custom_gap_y', 8)) * mm
else:
    # プリセット使用
    preset = LABEL_PRESETS.get(label_preset, LABEL_PRESETS['custom'])
    label_width = preset['width'] * mm
    label_height = preset['height'] * mm
    cols = preset['cols']
    rows = preset['rows']
    margin_left = preset['margin_left'] * mm
    margin_top = preset['margin_top'] * mm
    gap_x = preset['gap_x'] * mm
    gap_y = preset['gap_y'] * mm
```

### 3.3 UI実装

**ファイル**: `app/templates/labels/preview.html`

#### プリセット選択ドロップダウン

```html
<div class="mb-3">
    <label class="form-label">ラベル用紙</label>
    <select name="label_preset" class="form-select" id="labelPreset">
        <option value="custom">カスタムサイズ</option>
        <optgroup label="A-ONE製品">
            {% for key, preset in label_presets.items() %}
                {% if key != 'custom' %}
                    <option value="{{ key }}">{{ preset.name }}</option>
                {% endif %}
            {% endfor %}
        </optgroup>
    </select>
    <small class="form-text text-muted">使用するラベル用紙を選択してください</small>
</div>
```

#### カスタムサイズ設定欄

```html
<div id="customSizeSettings" class="mb-3 border p-3 bg-light">
    <h6 class="mb-3">カスタムサイズ設定</h6>
    <div class="row">
        <div class="col-md-6 mb-2">
            <label class="form-label">ラベル幅 (mm)</label>
            <input type="number" name="custom_width" class="form-control" value="90" step="0.1" min="10">
        </div>
        <div class="col-md-6 mb-2">
            <label class="form-label">ラベル高さ (mm)</label>
            <input type="number" name="custom_height" class="form-control" value="60" step="0.1" min="10">
        </div>
        <!-- 他の設定項目 -->
    </div>
</div>
```

#### JavaScriptによる動的制御

```javascript
// プリセット選択時の処理
document.getElementById('labelPreset').addEventListener('change', function() {
    const presetKey = this.value;
    const customSettings = document.getElementById('customSizeSettings');
    const labelCountDesc = document.getElementById('labelCountDescription');

    if (presetKey === 'custom') {
        // カスタムサイズの場合、設定欄を表示
        customSettings.style.display = 'block';

        const cols = parseInt(document.querySelector('input[name="custom_cols"]').value) || 2;
        const rows = parseInt(document.querySelector('input[name="custom_rows"]').value) || 4;
        const labelsPerPage = cols * rows;
        labelCountDesc.textContent = `A4用紙1枚につき${labelsPerPage}枚のラベルが印刷されます`;
    } else {
        // プリセットの場合、設定欄を非表示
        customSettings.style.display = 'none';

        // プリセットの情報を表示
        const preset = labelPresets[presetKey];
        const labelsPerPage = preset.cols * preset.rows;
        labelCountDesc.textContent = `A4用紙1枚につき${labelsPerPage}面のラベルが印刷されます (${preset.width}mm × ${preset.height}mm)`;
    }
});
```

---

## 4. 使い方

### 4.1 A-ONE製品プリセットの使用

1. **ラベル作成ページを開く**
   - レシピ詳細ページから「ラベル作成」ボタンをクリック

2. **ラベル用紙を選択**
   - 「ラベル用紙」ドロップダウンから使用するA-ONE製品を選択
   - 例：「A-ONE 31531 (12面)」を選択

3. **その他の設定**
   - 製造日を入力
   - 印刷枚数を入力
   - 必要に応じて原価・販売価格の表示を選択

4. **PDFをダウンロード**
   - 「PDFをダウンロード」ボタンをクリック
   - A-ONE用紙に合わせたラベルPDFが生成されます

### 4.2 カスタムサイズの使用

1. **カスタムサイズを選択**
   - 「ラベル用紙」ドロップダウンで「カスタムサイズ」を選択

2. **サイズを設定**
   - ラベル幅・高さを入力（mm単位）
   - 列数・行数を入力
   - 余白・間隔を調整

3. **プレビュー確認**
   - 右側のプレビューでラベルの大まかなイメージを確認
   - 1ページあたりの面数が自動表示されます

4. **PDFを生成**
   - 設定に基づいたラベルPDFが生成されます

---

## 5. 動作確認

### テスト結果

✅ **A-ONE製品プリセット**
- 31531 (12面) - 正常に印刷確認済み
- 72210 (10面) - レイアウト確認済み
- 28918 (8面) - レイアウト確認済み
- その他のプリセットも正常動作

✅ **カスタムサイズ**
- 任意のサイズでPDF生成可能
- 列数・行数の変更が反映される
- 余白・間隔の調整が正確

✅ **UI動作**
- プリセット選択時にカスタム設定欄が非表示になる
- カスタム選択時に設定欄が表示される
- 面数の自動計算が正確

---

## 6. 修正ファイル一覧

### 修正ファイル

1. **`app/routes/labels.py`**
   - LABEL_PRESETSディクショナリを追加（17-113行目）
   - preview関数でプリセットデータを渡すように修正（147行目）
   - generate関数でラベルサイズ設定を処理（157-187行目）

2. **`app/templates/labels/preview.html`**
   - ラベル用紙選択ドロップダウンを追加（15-28行目）
   - カスタムサイズ設定欄を追加（30-66行目）
   - JavaScript実装（175-217行目）

### 新規作成

- **`LABEL_SIZE_CUSTOMIZATION_FEATURE.md`** - 本ドキュメント

---

## 7. A-ONE製品の詳細仕様

### 推奨用途

| 品番 | 面数 | サイズ | 推奨用途 |
|------|------|--------|----------|
| 31531 | 12面 | 86.4×42.3mm | 商品表示ラベル（中サイズ） |
| 72210 | 10面 | 86.4×50.8mm | 商品表示ラベル（大サイズ）、材料名が多い商品 |
| 31538 | 21面 | 70.0×42.3mm | 商品表示ラベル（小サイズ）、シンプルな商品 |
| 28918 | 8面 | 99.0×67.5mm | 詳細表示ラベル、アレルゲン情報が多い商品 |
| 28729 | 18面 | 63.5×46.6mm | 小型商品向けラベル |
| 28315 | 24面 | 66.0×33.9mm | 小型商品、値札 |
| 28765 | 65面 | 38.1×21.2mm | インデックス、管理用ラベル |

### ラベル配置の精度

各プリセットは、A-ONE製品の公式仕様に基づいて設定されています：
- ラベルサイズ：製品仕様通り
- 余白：用紙の印刷可能領域を考慮
- 間隔：隣接ラベルとの間隔を正確に反映

**注意**: プリンターの機種や設定によって、わずかなズレが生じる場合があります。初回印刷時は試し印刷をお勧めします。

---

## 8. カスタムサイズ設定のヒント

### 用紙サイズの計算方法

A4用紙（210mm × 297mm）に最適な配置を計算する方法：

```
利用可能幅 = 210mm - 左余白 - 右余白（通常は左余白と同じ）
利用可能高さ = 297mm - 上余白 - 下余白（通常は上余白と同じ）

列数 = (利用可能幅 + 横間隔) / (ラベル幅 + 横間隔)
行数 = (利用可能高さ + 縦間隔) / (ラベル高さ + 縦間隔)
```

### 一般的な余白設定

- **標準プリンター**: 左右15mm、上下20mm
- **フチなし印刷対応**: 左右5mm、上下10mm
- **高精度プリンター**: 左右10mm、上下15mm

### トラブルシューティング

**ラベルがズレる場合**:
1. プリンターのプロパティで「実際のサイズ」または「100%」を選択
2. 「ページに合わせる」や「自動調整」をオフに
3. 余白設定を微調整（0.5mm単位で調整）

**ラベルが用紙からはみ出る場合**:
1. 余白を大きくする
2. ラベルサイズを小さくする
3. 列数・行数を減らす

---

## 9. 今後の拡張案

### 追加予定機能

1. **プリセットのカスタマイズ**
   - よく使うカスタム設定を保存
   - レシピごとにデフォルトラベルを設定

2. **他メーカー対応**
   - エーワン以外のメーカー（コクヨ、ヒサゴなど）
   - 海外製品（Avery等）

3. **プレビュー機能の強化**
   - 実際のラベル配置をビジュアル表示
   - 印刷前の確認機能

4. **QRコード対応**
   - 商品情報をQRコードで埋め込み
   - トレーサビリティ対応

---

## 10. まとめ

本機能により、以下が実現されました：

1. **市販ラベル用紙への対応**
   - A-ONE製品7種類にすぐに印刷可能
   - コスト削減（既製品の活用）

2. **柔軟なカスタマイズ**
   - 任意のサイズ・レイアウトに対応
   - ベーカリーの個別ニーズに対応

3. **使いやすいUI**
   - プリセット選択で簡単操作
   - カスタム設定も直感的

4. **実用性の向上**
   - 実際に印刷して確認済み
   - プリンター精度に配慮した設計

これにより、ベーカリー事業者は市販のラベル用紙を活用して、コスト効率よく商品ラベルを印刷できるようになりました。

---

**作成者**: Claude Code (AI Assistant)
**作成日**: 2025-10-27
**ステータス**: 完了・テスト済み
**テスト環境**: Windows, Flask開発サーバー
**実機テスト**: A-ONE 31531 (12面) で印刷確認済み
