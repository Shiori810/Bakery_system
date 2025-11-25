# インストール・起動ガイド（詳細版）

## 環境確認

まず、Pythonがインストールされているか確認してください。

### コマンドプロンプトを開く

1. Windows キー + R を押す
2. `cmd` と入力してEnter
3. 以下のコマンドを実行：

```cmd
python --version
```

または

```cmd
py --version
```

**Python 3.8以上が表示されればOKです。**

表示されない場合は、Pythonをインストールしてください：
https://www.python.org/downloads/

## インストール手順

### 方法1: start.bat を使用（推奨）

1. エクスプローラーで `bakery_cost_calculator` フォルダを開く
2. `start.bat` をダブルクリック
3. 黒い画面（コマンドプロンプト）が開きます
4. 初回は以下が自動実行されます：
   - 仮想環境の作成（1分程度）
   - パッケージのインストール（2-3分程度）
5. 「アプリケーションを起動しています...」と表示されたら成功
6. ブラウザで `http://localhost:5000` を開く

### 方法2: 手動インストール

#### ステップ1: コマンドプロンプトを開く

```cmd
cd C:\Users\ibuto\pan\bakery_cost_calculator
```

#### ステップ2: Pythonのバージョンを確認

```cmd
python --version
```

または

```cmd
py --version
```

#### ステップ3: 仮想環境を作成

```cmd
python -m venv venv
```

または

```cmd
py -m venv venv
```

**エラーが出る場合:**
```cmd
python -m pip install --upgrade pip
```

#### ステップ4: 仮想環境を有効化

```cmd
venv\Scripts\activate
```

成功すると、プロンプトの先頭に `(venv)` が表示されます：
```
(venv) C:\Users\ibuto\pan\bakery_cost_calculator>
```

#### ステップ5: pipをアップグレード

```cmd
python -m pip install --upgrade pip
```

#### ステップ6: 依存パッケージをインストール

```cmd
pip install -r requirements.txt
```

これには2-5分かかります。以下のようなメッセージが表示されます：
```
Collecting Flask==3.0.0
Downloading Flask-3.0.0-py3-none-any.whl
...
Successfully installed Flask-3.0.0 ...
```

#### ステップ7: インストール確認

```cmd
python check_install.py
```

すべてに ✓ が付けばOKです。

#### ステップ8: アプリケーションを起動

```cmd
python run.py
```

以下のように表示されれば成功です：
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

#### ステップ9: ブラウザでアクセス

ブラウザで以下のURLを開く：
```
http://localhost:5000
```

または
```
http://127.0.0.1:5000
```

## よくあるエラーと対処法

### エラー1: 'python' は、内部コマンドまたは外部コマンド...

**原因:** Pythonがインストールされていない、またはPATHが通っていない

**対処法:**
1. `py` コマンドを試す：
   ```cmd
   py --version
   py -m venv venv
   ```

2. それでもダメな場合、Pythonを再インストール：
   - https://www.python.org/downloads/ からダウンロード
   - インストール時に「Add Python to PATH」にチェック

### エラー2: Cannot create a file when that file already exists

**原因:** 仮想環境が既に存在する

**対処法:**
```cmd
rmdir /s venv
python -m venv venv
```

### エラー3: pip install でエラー

**原因:** pipが古い

**対処法:**
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### エラー4: Address already in use (ポート5000が使用中)

**原因:** 他のアプリケーションがポート5000を使用している

**対処法:**

方法A: 別のポートを使用
`run.py` の最終行を編集：
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # 5000 → 8000
```

その後、`http://localhost:8000` でアクセス

方法B: 使用中のプロセスを終了
```cmd
netstat -ano | findstr :5000
taskkill /PID <表示されたPID> /F
```

### エラー5: ModuleNotFoundError: No module named 'flask'

**原因:** 仮想環境が有効化されていない、またはパッケージ未インストール

**対処法:**
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### エラー6: 仮想環境を有効化できない（スクリプトの実行が無効）

**原因:** PowerShellの実行ポリシー

**対処法:**

PowerShellを管理者として開き：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

その後、再度：
```cmd
venv\Scripts\activate
```

## 完全な再インストール手順

すべてリセットして最初からやり直す場合：

```cmd
# 1. ディレクトリに移動
cd C:\Users\ibuto\pan\bakery_cost_calculator

# 2. 既存の仮想環境を削除
rmdir /s venv

# 3. 既存のデータベースを削除（オプション）
rmdir /s instance

# 4. 仮想環境を作成
python -m venv venv

# 5. 仮想環境を有効化
venv\Scripts\activate

# 6. pipをアップグレード
python -m pip install --upgrade pip

# 7. パッケージをインストール
pip install -r requirements.txt

# 8. 起動
python run.py
```

## 起動成功の確認

以下が表示されていれば成功です：

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

ブラウザで `http://localhost:5000` を開いてください。

## 次のステップ

起動できたら：

1. **新規登録** - トップページから店舗を登録
2. **ログイン** - 作成したアカウントでログイン
3. **設定** - 原価計算の設定を行う
4. **材料登録** - 使用する材料を登録
5. **レシピ作成** - 商品のレシピを作成

詳しくは [START_HERE.md](START_HERE.md) を参照してください。

## サポート

それでも起動できない場合は、以下の情報を確認してください：

1. Pythonのバージョン: `python --version`
2. pipのバージョン: `pip --version`
3. エラーメッセージの全文
4. 実行したコマンド

---

**起動できましたら、ぜひアプリをお楽しみください！**
