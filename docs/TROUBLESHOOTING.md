# トラブルシューティングガイド

## 接続が拒否される場合

### 原因1: アプリケーションが起動していない

**確認方法:**
コマンドプロンプトやターミナルで `python run.py` を実行した際に、以下のようなメッセージが表示されているか確認してください：

```
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```

**対処法:**

1. **Pythonがインストールされているか確認**
   ```bash
   python --version
   ```
   Python 3.8以上が必要です。

2. **依存パッケージをインストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **インストール確認スクリプトを実行**
   ```bash
   python check_install.py
   ```

### 原因2: ポートが既に使用されている

**エラーメッセージ例:**
```
OSError: [Errno 98] Address already in use
```

**対処法:**

1. **別のポートを使用する**

   `run.py` の最終行を編集：
   ```python
   # 5000 → 8000 に変更
   app.run(debug=True, host='0.0.0.0', port=8000)
   ```

   その後、`http://localhost:8000` でアクセス

2. **使用中のポートを確認して終了**

   Windows:
   ```bash
   netstat -ano | findstr :5000
   taskkill /PID <プロセスID> /F
   ```

   macOS/Linux:
   ```bash
   lsof -i :5000
   kill -9 <PID>
   ```

### 原因3: ファイアウォールがブロックしている

**対処法:**

1. Windows Defenderファイアウォールの設定を確認
2. Pythonの通信を許可する
3. または、ローカルホストのみでアクセス: `http://127.0.0.1:5000`

### 原因4: 仮想環境が有効化されていない

**確認方法:**
コマンドプロンプトの先頭に `(venv)` が表示されているか確認

**対処法:**

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

## よくあるエラーと対処法

### ImportError: No module named 'flask'

**原因:** Flaskがインストールされていない

**対処法:**
```bash
pip install flask
# または
pip install -r requirements.txt
```

### ModuleNotFoundError: No module named 'app'

**原因:** 間違ったディレクトリで実行している

**対処法:**
`bakery_cost_calculator` ディレクトリに移動してから実行：
```bash
cd bakery_cost_calculator
python run.py
```

### SQLAlchemy関連のエラー

**エラーメッセージ例:**
```
(sqlite3.OperationalError) unable to open database file
```

**対処法:**

1. `instance` ディレクトリが存在するか確認
   ```bash
   mkdir instance
   ```

2. データベースファイルの権限を確認

3. データベースを再作成
   ```bash
   rm instance/bakery.db
   python run.py
   ```

### PDF生成でエラーが出る

**エラーメッセージ例:**
```
TTFError: Can't find font file
```

**原因:** 日本語フォントが見つからない

**対処法:**

`app/routes/labels.py` の `register_fonts()` 関数を編集：

Windows以外の場合:
```python
def register_fonts():
    """日本語フォントの登録"""
    try:
        # macOSの場合
        font_path = '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
        # または Linuxの場合
        # font_path = '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'

        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Japanese', font_path))
            return 'Japanese'
    except:
        pass

    return 'Helvetica'
```

### ブラウザで404エラーが表示される

**原因:** URLが間違っている

**対処法:**

正しいURL:
- トップページ: `http://localhost:5000/`
- ログイン: `http://localhost:5000/auth/login`
- 登録: `http://localhost:5000/auth/register`

## 起動方法まとめ

### 方法1: start.batを使用（Windows推奨）

1. `start.bat` をダブルクリック
2. 自動的に仮想環境の作成とパッケージインストールが行われます

### 方法2: 手動で起動

```bash
# 1. ディレクトリに移動
cd bakery_cost_calculator

# 2. 仮想環境を作成（初回のみ）
python -m venv venv

# 3. 仮想環境を有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. パッケージをインストール（初回のみ）
pip install -r requirements.txt

# 5. アプリケーションを起動
python run.py
```

### 方法3: 仮想環境なしで起動（非推奨）

```bash
pip install -r requirements.txt
python run.py
```

## デバッグモード

詳細なエラー情報を表示するには、`run.py` で `debug=True` が設定されていることを確認してください：

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

エラーが発生した際に、詳細なスタックトレースがブラウザに表示されます。

## それでも解決しない場合

1. **Python環境を確認**
   ```bash
   python --version
   pip --version
   ```

2. **インストール確認スクリプトを実行**
   ```bash
   python check_install.py
   ```

3. **エラーメッセージの全文を記録**

   コマンドプロンプト/ターミナルに表示されるエラーメッセージを保存

4. **ログを確認**

   アプリケーション起動時のコンソール出力を確認

5. **環境を再構築**
   ```bash
   # 仮想環境を削除
   rm -rf venv  # macOS/Linux
   rmdir /s venv  # Windows

   # 最初から再実行
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   python run.py
   ```

## お問い合わせ

上記の方法で解決しない場合は、以下の情報を添えてお問い合わせください：

- OS（Windows/macOS/Linux）とバージョン
- Pythonバージョン
- エラーメッセージの全文
- 実行したコマンド
- `check_install.py` の実行結果
