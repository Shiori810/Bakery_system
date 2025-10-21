# クイックスタートガイド

## すぐに始める方法

### Windows環境での起動

```powershell
# 1. プロジェクトディレクトリに移動
cd bakery_cost_calculator

# 2. 仮想環境を作成
python -m venv venv

# 3. 仮想環境を有効化
venv\Scripts\activate

# 4. 依存パッケージをインストール
pip install -r requirements.txt

# 5. アプリケーションを起動
python run.py
```

### macOS/Linux環境での起動

```bash
# 1. プロジェクトディレクトリに移動
cd bakery_cost_calculator

# 2. 仮想環境を作成
python3 -m venv venv

# 3. 仮想環境を有効化
source venv/bin/activate

# 4. 依存パッケージをインストール
pip install -r requirements.txt

# 5. アプリケーションを起動
python run.py
```

## アクセス方法

起動後、ブラウザで以下のURLにアクセスしてください：

```
http://localhost:5000
```

## 初回利用の流れ

1. **店舗登録** - トップページから新規登録
2. **ログイン** - 登録したアカウントでログイン
3. **設定** - 原価計算の設定（人件費・光熱費・利益率）
4. **材料登録** - 使用する材料を登録
5. **レシピ作成** - 商品のレシピを作成
6. **原価確認** - 自動計算された原価を確認
7. **ラベル印刷** - 商品ラベルをPDF出力

## トラブルシューティング

### Python が見つからない場合

Pythonがインストールされていない場合は、以下からダウンロードしてインストールしてください：
https://www.python.org/downloads/

### ポートが使用中の場合

`run.py` の最終行を編集して別のポートを使用してください：

```python
app.run(debug=True, host='0.0.0.0', port=8000)  # 5000 → 8000に変更
```

### PDF生成でエラーが出る場合

Windows以外の環境では、日本語フォントのパスを変更する必要があります。
`app/routes/labels.py` の `register_fonts()` 関数を編集してください。

## 詳細情報

詳しい使い方については [README.md](README.md) を参照してください。
