# 2025-10-29 ラベル印刷機能の改善作業レポート

## 作業概要
A-ONE 31538ラベル用紙への印刷品質を大幅に改善し、本番環境での日本語文字化け問題に対応しました。

## 実施した改善項目

### 1. ラベル余白の調整
**問題:**
- A-ONE 31538で印刷すると上と左に余白があり、右端が見切れていた
- 商品名の上部が印刷時に切れていた
- 店舗名の行がラベルからはみ出していた

**解決策:**
- A-ONE 31538の余白を0に設定（`margin_left: 0`, `margin_top: 0`）
- A-ONE 31538は70mm × 3列 = 210mm（A4幅ピッタリ）の余白なし用紙
- 商品名開始位置を調整: `y + height - padding - 1mm`

**ファイル:** [app/routes/labels.py](../app/routes/labels.py) 行53-64, 345

**コミット:**
- `a2892f3` - Fix: Correct A-ONE 31538 margins to fit 3 columns on A4 paper
- `978a4e8` - Fix: Move entire label content up by 3mm to fit store name

### 2. 黒い枠線の削除
**問題:**
- ラベル周囲に不要な黒い枠線が表示されていた

**解決策:**
- `draw_label()` 関数から枠線描画コード（`setStrokeColorRGB`, `setLineWidth`, `rect`）を削除

**ファイル:** [app/routes/labels.py](../app/routes/labels.py) 行246-252（削除前）

**コミット:** `a130816` - Remove black border from PDF labels

### 3. 材料名の複数行折り返し
**問題:**
- 材料が多い場合、ラベルの横幅からはみ出していた

**解決策:**
- `split_japanese_text()` 関数を新規実装
- 材料の区切り文字「、」を考慮して適切に折り返し
- 最大6行まで表示（従来の4行から増加）

**ファイル:** [app/routes/labels.py](../app/routes/labels.py) 行61-109

**コミット:** `d5791e7` - Fix: Wrap long ingredient text across multiple lines in labels

### 4. 店舗名の表示位置調整
**問題:**
- 店舗名が罫線と重なっていた
- 販売価格と同じ行に表示したい

**解決策:**
- 店舗名を販売価格と同じ行の右端に配置
- `current_y` を使用した相対位置で配置

**ファイル:** [app/routes/labels.py](../app/routes/labels.py) 行419-447

**コミット:**
- `d106d43` - Fix: Position store name to avoid overlapping with separator lines
- `8636402` - Fix: Display store name on same line as selling price

### 5. 【材料】見出しの改善
**問題:**
- 【材料】見出しの下に材料が表示されていた

**解決策:**
- 【材料】のすぐ隣から材料を表示開始
- 1行目：見出しと材料を同じ行に表示
- 2行目以降：材料のみを表示

**ファイル:** [app/routes/labels.py](../app/routes/labels.py) 行366-397

**コミット:** `25c9bbe` - Fix: Display ingredients immediately after 【材料】 label on same line

### 6. 商品名のフォントサイズと折り返し
**問題:**
- 商品名のフォントが大きすぎた（14pt）
- 長い商品名がラベル幅からはみ出していた

**解決策:**
- フォントサイズを14pt → 10ptに変更（材料7ptより大きく）
- `split_text_by_width()` 関数を実装（1文字ずつ幅を計算）
- 最大3行まで自動折り返し

**ファイル:** [app/routes/labels.py](../app/routes/labels.py) 行17-58, 347-357

**コミット:**
- `e51a2a5` - Fix: Adjust product name font size and add multi-line wrapping
- `9a356ef` - Fix: Product name text wrapping to fit within label width

### 7. 余白の最適化
**問題:**
- 商品名と罫線の間、賞味期限の下に不要な余白があった

**解決策:**
- 商品名と罫線の間の余白（1mm）を削除
- 商品名の行間を4mm → 3.5mmに縮小
- 賞味期限の下の余白（1mm）を削除

**ファイル:** [app/routes/labels.py](../app/routes/labels.py) 行357-359, 418

**コミット:**
- `47b022b` - Fix: Remove spacing between product name and separator line
- `0ab40b0` - Fix: Remove extra spacing below expiration date

### 8. 本番環境の日本語文字化け対応（未解決）
**問題:**
- 本番環境（Render/Linux）でラベルPDFの日本語が文字化けする
- Windowsフォント（MSゴシック等）が本番環境に存在しない

**試みた解決策:**

#### 試行1: Variable Font（失敗）
- Noto Sans JP Variable Font（9.3MB）を追加
- 本番環境でサーバーエラー発生
- ファイルサイズが大きすぎた可能性

**コミット:** `1665618` - Fix: Add Noto Sans JP font for production environment（後に削除）

#### 試行2: 緊急復旧
- フォントファイルを削除して本番環境を復旧
- 材料登録機能は復旧したが、ラベルPDFは文字化け

**コミット:** `4aedd67` - Revert: Remove font file to fix production server error

#### 試行3: OTFファイル（誤り）
- Noto Sans JP OTF（286KB）をダウンロード
- `.ttf` 拡張子で保存（誤り）
- ReportLabがOTFを正しく読み込めず文字化け継続

**コミット:** `a7e918c` - Fix: Add Noto Sans JP font for production environment (OTF version)

#### 試行4: 正しいTTFファイル + 詳細ログ
- Google Fontsから正しいTTF形式をダウンロード（286KB）
- フォント読み込みの詳細ログを追加
- Windowsフォント優先、プロジェクト内フォントをフォールバック

**ファイル:**
- [app/static/fonts/NotoSansJP-Regular.ttf](../app/static/fonts/NotoSansJP-Regular.ttf) - 286KB
- [app/routes/labels.py](../app/routes/labels.py) 行211-258

**コミット:**
- `f42f1fd` - Fix: Replace with correct TTF format Noto Sans JP font
- `93eff6f` - Merge: Combine font configurations from both branches
- `eb59f80` - Debug: Add detailed font loading logs

**現在の状態:**
- 再デプロイ済みだが文字化け継続
- 次のステップ: Renderログを確認して原因特定

### フォント登録ロジック（最終版）

```python
def register_fonts():
    """日本語フォントの登録"""
    # プロジェクト内のフォントパス（本番環境用）
    app_font_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'NotoSansJP-Regular.ttf')
    app_font_path = os.path.abspath(app_font_path)

    # Windows/Linux両方で利用可能な日本語フォントを順に試す
    font_candidates = [
        # Windows で利用可能なフォント（ローカル環境優先）
        ('C:/Windows/Fonts/msgothic.ttc', 0),  # MSゴシック
        ('C:/Windows/Fonts/msmincho.ttc', 0),  # MS明朝
        ('C:/Windows/Fonts/meiryo.ttc', 0),    # メイリオ
        ('C:/Windows/Fonts/msgothic.ttc', None),
        ('C:/Windows/Fonts/YuGothM.ttc', 0),   # 游ゴシック Medium
        ('C:/Windows/Fonts/YuGothB.ttc', 0),   # 游ゴシック Bold
        # プロジェクト内のフォント（本番環境用、286KB）
        (app_font_path, None),  # Noto Sans JP TTF
        # Linux (Render環境) で利用可能なシステムフォント
        ('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc', 0),
        ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 0),
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', None),
    ]
```

## レイアウト改善の結果

### フォントサイズ階層
- 商品名: 10pt
- 【材料】: 8pt
- 材料: 7pt
- その他テキスト: 7pt
- 店舗名: 6pt

### レイアウト例
```
国産小麦とカリフォルニア
レーズンのロールパン
──────────────
【材料】強力粉、無塩バター、砂糖、食塩、水、
ドライイースト、薄力粉

アレルゲン: 小麦、乳

製造日: 2025年10月29日
賞味期限: 2025年10月30日
──────────────
販売価格: 100円        satoe
```

## 技術的な詳細

### 新規実装関数

#### 1. `split_text_by_width()` - 商品名用折り返し
```python
def split_text_by_width(canvas_obj, text, font_name, font_size, max_width):
    """
    テキストを指定した幅に収まるように1文字ずつ分割する（商品名用）
    """
    # 1文字ずつ幅を計算して、ラベル幅内に収まるように分割
    # 日本語・英数字混在でも正確に動作
```

#### 2. `split_japanese_text()` - 材料用折り返し
```python
def split_japanese_text(canvas_obj, text, font_name, font_size, max_width):
    """
    日本語テキストを指定した幅に収まるように分割する（材料用）
    """
    # 材料を「、」で分割して、適切に折り返し
    # 各材料名が途中で切れないように配慮
```

## A-ONE 31538 仕様
- 製品名: A-ONE 31538 (21面)
- ラベルサイズ: 70mm × 42.3mm
- レイアウト: 3列 × 7行 = 21面
- 用紙サイズ: A4 (210mm × 297mm)
- 余白: 上下左右すべて 0mm（余白なし用紙）
- ラベル間隔: 0mm

## プリンター設定推奨事項（OKI MC863）

1. **PDFビューアの設定:**
   - 「ページサイズ処理」で「実際のサイズ」を選択
   - 「用紙に合わせる」や「Fit to page」は選択しない

2. **印刷倍率:**
   - 100%で印刷（拡大縮小しない）

3. **理由:**
   - A-ONE 31538は精密にカットされた余白なし用紙
   - 拡大縮小がかかると、ラベル位置がずれる

## Git コミット履歴

```
eb59f80 - Debug: Add detailed font loading logs
f42f1fd - Fix: Replace with correct TTF format Noto Sans JP font
93eff6f - Merge: Combine font configurations from both branches
978a4e8 - Fix: Move entire label content up by 3mm to fit store name
04300db - Fix: Increase top margin to 4mm to prevent text cutoff
1c7e91f - Fix: Add top margin to prevent product name from being cut off
47b022b - Fix: Remove spacing between product name and separator line
0ab40b0 - Fix: Remove extra spacing below expiration date
9a356ef - Fix: Product name text wrapping to fit within label width
e51a2a5 - Fix: Adjust product name font size and add multi-line wrapping
25c9bbe - Fix: Display ingredients immediately after 【材料】 label on same line
8636402 - Fix: Display store name on same line as selling price
d106d43 - Fix: Position store name to avoid overlapping with separator lines
d5791e7 - Fix: Wrap long ingredient text across multiple lines in labels
4aedd67 - Revert: Remove font file to fix production server error
35f05af - Rename CUSTOM_DOMAIN_SETUP_DISCUSSION.md to include date
63d3912 - Add documentation for label printing fixes (2025-10-29)
a130816 - Remove black border from PDF labels
a2892f3 - Fix: Correct A-ONE 31538 margins to fit 3 columns on A4 paper
```

## 未解決の課題

### 本番環境の日本語文字化け（最優先）

**現状:**
- ローカル環境: 正常動作（Windowsフォント使用）
- 本番環境: 文字化け継続

**次のステップ:**
1. Renderのログを確認（デプロイ後にラベルPDF生成）
2. ログで `[Font]` を検索して、どのフォントが使われているか確認
3. 以下のいずれかが表示される:
   - `[Font] Successfully registered: ...` → フォント読み込み成功
   - `[Font] Failed to register ...` → フォント読み込み失敗
   - `[Font] WARNING: No Japanese font available` → すべて失敗

**想定される原因:**
1. フォントファイルがデプロイされていない
2. ファイルパスが間違っている（Linux環境のパス）
3. ファイル形式の問題（TTF/OTF/TTC）
4. ReportLabのバージョン問題

**試すべき対策:**
- Renderログでフォントパスを確認
- 本番環境でファイルの存在確認（`ls /app/app/static/fonts/`）
- より単純なフォント形式を試す
- Python requirements確認（reportlabバージョン）

## テスト方法

### ローカル環境
1. Flaskサーバーを再起動
2. http://localhost:5000 にアクセス
3. レシピのラベルプレビューページに移動
4. A-ONE 31538 (21面) を選択してPDF生成
5. OKI MC863で「実際のサイズ」印刷

### 本番環境
1. 詩織さんに再デプロイ依頼（最新コミット: eb59f80）
2. ラベルPDFを生成
3. Renderログを確認
4. 文字化けの有無を確認

## 関連ドキュメント

- [2025-10-29_LABEL_PRINTING_FIXES.md](2025-10-29_LABEL_PRINTING_FIXES.md) - 余白と枠線の修正
- [TEAM_COLLABORATION_SETUP.md](TEAM_COLLABORATION_SETUP.md) - Renderチーム共同開発
- [CUSTOM_DOMAIN_SETUP_DISCUSSION1028.md](../CUSTOM_DOMAIN_SETUP_DISCUSSION1028.md) - カスタムドメイン設定

## まとめ

### 達成した改善
✅ A-ONE 31538の余白設定を最適化（3列がピッタリ収まる）
✅ 黒い枠線を削除
✅ 材料名の複数行折り返し（最大6行）
✅ 店舗名を販売価格と同じ行に表示
✅ 【材料】見出しと材料を同じ行に表示
✅ 商品名のフォントサイズ調整（14pt → 10pt）
✅ 商品名の複数行折り返し（最大3行）
✅ 不要な余白を削除
✅ 印刷時の位置調整

### 残課題
❌ 本番環境の日本語文字化け（要Renderログ確認）

### 次回作業予定
1. Renderログを確認して文字化けの原因特定
2. 原因に応じた対策を実施
3. 本番環境で日本語表示を確認
4. 必要に応じてフォント読み込みロジックを再検討
