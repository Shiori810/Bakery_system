# Python インストールガイド

## 現在の状況

以下のエラーが発生しています：

```
'python' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

これは、**Pythonがインストールされていない、またはPATHが通っていない**ことを意味します。

## 📋 確認方法

1. `check_python.bat` をダブルクリック
2. 結果を確認

## 🔧 解決方法

### 方法1: Pythonをインストールする（推奨）

#### ステップ1: Pythonをダウンロード

1. https://www.python.org/downloads/ にアクセス
2. 黄色い「Download Python 3.x.x」ボタンをクリック
3. ダウンロードした `python-3.x.x-amd64.exe` を実行

#### ステップ2: インストール

**重要: 以下の設定を必ず行ってください**

1. インストーラーの最初の画面で：
   - ✅ **「Add Python to PATH」にチェックを入れる**（最重要！）
   - 「Install Now」をクリック

2. インストール完了を待つ（1-2分）

3. 「Close」をクリック

#### ステップ3: 確認

1. **コマンドプロンプトを閉じる**（重要！古いコマンドプロンプトではPATHが反映されません）

2. 新しくコマンドプロンプトを開く
   - Windows キー + R
   - `cmd` と入力
   - Enter

3. 以下を実行：
   ```cmd
   python --version
   ```

4. `Python 3.x.x` と表示されればOK！

#### ステップ4: アプリを起動

```cmd
cd C:\Users\ibuto\pan\bakery_cost_calculator
simple_start.bat
```

### 方法2: Microsoft Store版Pythonを使用

1. Windows キー を押す
2. 「Microsoft Store」を検索して開く
3. 「Python」を検索
4. 「Python 3.12」（または最新版）をインストール
5. インストール後、コマンドプロンプトを開く
6. `python --version` で確認

### 方法3: PATHを手動で設定する（上級者向け）

Pythonは既にインストールされているがPATHが通っていない場合：

#### Pythonのインストール場所を確認

一般的な場所：
- `C:\Users\ibuto\AppData\Local\Programs\Python\Python3xx\`
- `C:\Python3xx\`
- `C:\Program Files\Python3xx\`

#### PATHに追加

1. Windows キー + R → `sysdm.cpl` → Enter
2. 「詳細設定」タブ → 「環境変数」
3. 「システム環境変数」の「Path」を選択 → 「編集」
4. 「新規」をクリック
5. Pythonのインストールフォルダを追加
   - 例: `C:\Users\ibuto\AppData\Local\Programs\Python\Python312\`
6. もう一度「新規」をクリック
7. Scriptsフォルダも追加
   - 例: `C:\Users\ibuto\AppData\Local\Programs\Python\Python312\Scripts\`
8. 「OK」で閉じる
9. **コマンドプロンプトを再起動**

## 🚀 インストール後の起動手順

### 最も簡単な方法

```cmd
cd C:\Users\ibuto\pan\bakery_cost_calculator
simple_start.bat
```

`simple_start.bat` をダブルクリックしても同じです。

### 手動起動

```cmd
cd C:\Users\ibuto\pan\bakery_cost_calculator

# パッケージをインストール（初回のみ）
python -m pip install Flask Flask-SQLAlchemy Flask-Login Flask-WTF WTForms bcrypt reportlab python-dotenv

# 起動
python run.py
```

その後、ブラウザで `http://localhost:5000` を開く

## ❓ よくある質問

### Q: Pythonのどのバージョンをインストールすべきですか？

**A:** Python 3.8以上であればOKです。最新版（3.12や3.13）を推奨します。

### Q: 32bit版と64bit版、どちらをインストールすべきですか？

**A:** ほとんどの場合、64bit版を選んでください。お使いのPCが64bitであれば64bit版です。

### Q: pipとは何ですか？

**A:** Pythonのパッケージ管理ツールです。Pythonをインストールすると自動的に含まれます。

### Q: 仮想環境は必要ですか？

**A:** 必須ではありません。`simple_start.bat` は仮想環境なしで動作します。

### Q: Microsoft Store版とpython.org版、どちらが良いですか？

**A:** どちらでも動作します。python.org版の方が一般的です。

## 🔍 トラブルシューティング

### エラー: 'pip' は、内部コマンドまたは外部コマンド...

**対処法:**
```cmd
python -m pip --version
```

`python -m pip` を使ってpipを実行します。

### エラー: Python was not found

**対処法:**
1. コマンドプロンプトを再起動
2. それでもダメなら、Pythonを再インストール（「Add Python to PATH」にチェック）

### エラー: アクセスが拒否されました

**対処法:**
コマンドプロンプトを管理者として実行：
1. Windows キー
2. `cmd` と入力
3. 右クリック → 「管理者として実行」

## 📞 それでも解決しない場合

以下の情報を確認してください：

1. Windowsのバージョン
   ```cmd
   winver
   ```

2. Pythonの検索
   ```cmd
   where python
   where py
   ```

3. 環境変数PATH
   ```cmd
   echo %PATH%
   ```

これらの情報があれば、より詳細なサポートが可能です。

---

**Pythonをインストールできたら、`simple_start.bat` をダブルクリックしてアプリを起動してください！**
