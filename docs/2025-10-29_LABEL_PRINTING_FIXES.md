# 2025-10-29 ラベル印刷機能の修正

## 概要
A-ONE 31538 (21面) ラベル用紙への印刷における問題を修正しました。

## 実施した修正

### 1. A-ONE 31538の余白設定の修正

**問題:**
- PDFに上部と左部に余白が追加されていた
- 3列のラベルが用紙の右端で見切れていた
- A-ONE 31538は上下左右に余白がない用紙であるにも関わらず、margin設定が追加されていた

**原因:**
- `margin_top: 10.5mm` と `margin_left: 5mm` が設定されていた
- A-ONE 31538は 70mm × 3列 = 210mm（A4幅ピッタリ）の設計
- 左余白5mmを追加すると 215mm > 210mm となり、右端が切れる

**修正内容:**
`app/routes/labels.py` の A-ONE 31538設定を以下のように変更:

```python
'31538': {
    'name': 'A-ONE 31538 (21面)',
    'product_code': '31538',
    'width': 70.0,
    'height': 42.3,
    'cols': 3,
    'rows': 7,
    'margin_left': 0,  # 余白なし用紙
    'margin_top': 0,   # 余白なし用紙
    'gap_x': 0,
    'gap_y': 0
},
```

**ファイル:** [app/routes/labels.py](../app/routes/labels.py) 行53-64

**コミット:** `a2892f3` - "Fix: Correct A-ONE 31538 margins to fit 3 columns on A4 paper"

### 2. 黒い枠線の削除

**問題:**
- ラベルの周囲に黒い枠線が描画されていた
- 実際のラベル用紙にはミシン目があるため、枠線は不要

**修正内容:**
`draw_label()` 関数から枠線描画コードを削除:

削除したコード:
```python
# 枠線
c.setStrokeColorRGB(0, 0, 0)
c.setLineWidth(0.5)
c.rect(x, y, width, height)
```

**ファイル:** [app/routes/labels.py](../app/routes/labels.py) 行246-252（削除前）

**コミット:** `a130816` - "Remove black border from PDF labels"

## プリンター設定の推奨事項

### OKI MC863 での印刷設定

PDFを印刷する際は、以下の設定を使用してください:

1. **Adobe Reader / PDF閲覧ソフトの設定:**
   - 印刷ダイアログで「ページサイズ処理」または「Page Sizing & Handling」を確認
   - 「実際のサイズ」または「Actual size」を選択
   - 「用紙に合わせる」や「Fit to page」は選択しない

2. **印刷倍率:**
   - 100% で印刷（拡大縮小しない）
   - PDFは210mm × 297mm（A4サイズ）として生成されている

3. **理由:**
   - A-ONE 31538は精密にカットされた余白なし用紙
   - PDFに拡大縮小がかかると、ラベル位置がずれる
   - 1mm未満のずれでも、21面すべてのラベルが用紙からはみ出す可能性がある

## 技術的な詳細

### A-ONE 31538 仕様
- 製品名: A-ONE 31538 (21面)
- ラベルサイズ: 70mm × 42.3mm
- レイアウト: 3列 × 7行 = 21面
- 用紙サイズ: A4 (210mm × 297mm)
- 余白: 上下左右すべて 0mm
- ラベル間隔: 0mm

### PDF生成の計算
```
横方向: 70mm × 3列 = 210mm (A4幅)
縦方向: 42.3mm × 7行 = 296.1mm ≈ 297mm (A4高さ)
```

この計算により、A-ONE 31538は余白を一切設定せずに、A4用紙全面にラベルが配置される設計であることが分かります。

## 前回のセッションからの継続作業

前回のセッションでは以下の問題を修正していました:

1. **日本語フォントの文字化け修正** - TTC（TrueType Collection）ファイルのsubfontIndex指定
2. **店舗名の切れ修正** - テキスト幅チェックと自動切り詰め機能

これらの修正と合わせて、今回の余白と枠線の修正により、A-ONE 31538ラベル用紙への正確な印刷が可能になりました。

## テスト方法

1. ローカル環境でFlaskサーバーを起動
2. http://localhost:5000 にアクセス
3. レシピのラベルプレビューページに移動
4. ラベルプリセットで「A-ONE 31538 (21面)」を選択
5. PDFをダウンロード
6. OKI MC863で「実際のサイズ」設定で印刷
7. A-ONE 31538用紙に正確に印刷されることを確認

## 関連ドキュメント

- [TEAM_COLLABORATION_SETUP.md](TEAM_COLLABORATION_SETUP.md) - Renderチーム共同開発セットアップ
- [CUSTOM_DOMAIN_SETUP_DISCUSSION.md](CUSTOM_DOMAIN_SETUP_DISCUSSION.md) - カスタムドメイン設定の議論
- [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) - Renderデプロイガイド

## まとめ

今日の作業により、以下が達成されました:

✅ A-ONE 31538用紙の余白設定を0に修正（3列が210mm幅にピッタリ収まる）
✅ ラベルの黒い枠線を削除（よりクリーンな印刷結果）
✅ プリンター設定の推奨事項を文書化

これにより、A-ONE 31538ラベル用紙への正確な印刷が可能になりました。
