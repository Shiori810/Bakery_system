# ラベル日本語文字化け問題 修正レポート - 2025年10月31日

## 問題の概要

ラベル機能でPDFを生成すると、日本語テキストが文字化けする問題が発生していました。

## 症状

- ラベルPDFを生成した際に、商品名、材料、日付などの日本語が正しく表示されない
- 文字化け（「□□□」や意味不明な文字）が発生
- 過去の機能修正が影響しているのではないかとの懸念

## 調査結果

### 根本原因の特定

調査の結果、`app/static/fonts/NotoSansJP-Regular.ttf` が実際にはフォントファイルではなく、**GitHubの404エラーページ（HTML）**になっていることが判明しました。

```bash
# ファイルの内容を確認した結果
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Page not found · GitHub · GitHub</title>
...
```

### 原因の経緯

コミット履歴から、以下の流れで問題が発生したことが分かりました：

1. **2025-10-28頃** - コミット `a7e918c`: "Fix: Add Noto Sans JP font for production environment (OTF version)"
   - このコミットでフォントファイルを追加しようとした
   - しかし、GitHubのURLから直接ダウンロードしようとしたため、404エラーページがダウンロードされた

2. **2025-10-28頃** - コミット `93eff6f`: "Merge: Combine font configurations from both branches"
   - マージ時に問題のあるファイルがそのまま残された

3. **2025-10-31** - ラベル機能使用時に文字化けが発覚

### なぜ以前は動作していたのか

- ローカル開発環境（Windows）では、`labels.py` の `register_fonts()` 関数がWindowsシステムフォント（MSゴシック、メイリオなど）を優先して使用するため、問題が顕在化しなかった
- プロジェクト内のフォントファイルは最後の候補として設定されていたため、ローカルでは影響がなかった

```python
# labels.py の font_candidates より
font_candidates = [
    # Windows で利用可能なフォント（ローカル環境優先）
    ('C:/Windows/Fonts/msgothic.ttc', 0),  # MSゴシック
    ('C:/Windows/Fonts/msmincho.ttc', 0),  # MS明朝
    ('C:/Windows/Fonts/meiryo.ttc', 0),    # メイリオ
    ...
    # プロジェクト内のフォント（本番環境用、286KB）
    (app_font_path, None),  # <- ここが破損していた
]
```

### 他の機能修正との関連性

調査の結果、**他の機能修正（レイアウト調整、マージン調整など）は文字化けに影響していない**ことが確認されました。問題は純粋にフォントファイルの破損によるものでした。

## 修正内容

### 1. 破損ファイルの削除

```bash
rm c:\Users\ibuto\pan\bakery_cost_calculator\app\static\fonts\NotoSansJP-Regular.ttf
```

### 2. 正しいフォントファイルのダウンロード

Google Fonts公式リポジトリから正しいNoto Sans JP可変フォントをダウンロードしました：

```bash
# ダウンロード元
https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP[wght].ttf

# ファイル情報
- ファイル名: NotoSansJP-Regular.ttf
- ファイルサイズ: 9,589,900 bytes (約9.6MB)
- 形式: Variable Font (可変フォント)
```

### 3. 動作確認

以下のテストを実施し、正常動作を確認しました：

1. **フォント登録テスト**
   ```python
   pdfmetrics.registerFont(TTFont('Japanese', font_path))
   # -> OK: Font registered successfully!
   ```

2. **PDF生成テスト**
   - 日本語テキストを含むテストPDFを生成
   - 「商品名：クロワッサン」「材料：小麦粉、バター、砂糖、塩」などが正しく表示されることを確認

## 修正後の動作

- ラベルPDFで日本語が正しく表示される
- Windowsローカル環境では引き続きシステムフォントを優先使用
- Linux本番環境では、正しいNoto Sans JPフォントが使用される

## 今後の予防策

### 1. フォントファイルの検証

フォントファイルを追加/更新する際は、以下を確認すること：

```bash
# ファイルの実体を確認
file app/static/fonts/NotoSansJP-Regular.ttf
# または
head -n 1 app/static/fonts/NotoSansJP-Regular.ttf
# HTMLの場合は "<!DOCTYPE html>" が表示される
```

### 2. ダウンロード方法の明確化

GitHubからファイルをダウンロードする際は、**Rawボタン経由**で正しいURLを使用すること：

- ❌ NG: `https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansJP-Regular.otf`
  （このURLは404エラーになる）

- ✅ OK: `https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP[wght].ttf`
  （正しいリポジトリと正しいパス）

### 3. フォント読み込みのエラーハンドリング

`labels.py` の `register_fonts()` 関数は既に適切なエラーハンドリングを実装済み：

```python
for font_path, subfont_index in font_candidates:
    try:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Japanese', font_path))
            print(f"[Font] Successfully registered: {font_path}")
            return 'Japanese'
    except Exception as e:
        print(f"[Font] Failed to register {font_path}: {e}")
        continue
```

このため、将来的にフォントファイルに問題があった場合でも、ログから問題を特定できます。

## コミット情報

```
コミットハッシュ: ea32cc3
コミットメッセージ: Fix: Replace corrupted font file with valid Noto Sans JP font
日付: 2025-10-31
```

## 影響範囲

- **影響を受けた機能**: ラベルPDF生成機能のみ
- **影響を受けなかった機能**: レシピ管理、原価計算、販売価格設定など、その他すべての機能
- **データへの影響**: なし（フォントファイルのみの問題）

## まとめ

ラベル機能の日本語文字化け問題は、フォントファイルが実際にはHTMLページとして保存されていたことが原因でした。正しいフォントファイルをダウンロードして置き換えることで問題を解決しました。

他の機能修正との関連性はなく、純粋にフォントファイルの破損による問題でした。今後は、バイナリファイルを追加する際に、ファイルの実体を確認するプロセスを導入することで、同様の問題を予防できます。

---

**作成日**: 2025年10月31日
**作成者**: Claude Code
**対象バージョン**: commit ea32cc3
