# 詩織さんと一緒にVSCodeで開発する方法

## 🚀 最短5分で始められるリアルタイム共同編集

VSCode Live Shareを使うと、**まるで隣に座って一緒にコードを書いているように**開発できます！

---

## ステップ1: 準備（両者共通）5分

### 1-A. リポジトリをクローン

```bash
git clone https://github.com/Shiori810/Bakery_system.git
cd Bakery_system
```

### 1-B. VSCodeで開く

```bash
code .
```

### 1-C. Live Share拡張機能をインストール

**VSCode内から:**
1. 左サイドバーの拡張機能アイコンをクリック（`Ctrl+Shift+X`）
2. 検索欄に「**Live Share**」と入力
3. 「**Live Share Extension Pack**」を見つけてインストール

**またはコマンドライン:**
```bash
code --install-extension MS-vsliveshare.vsliveshare
```

### 1-D. GitHubでサインイン

1. VSCode下部のステータスバーに「**Live Share**」ボタンが表示される
2. クリックしてGitHubアカウントでサインイン

---

## ステップ2: セッション開始

### 👤 ホスト側（詩織さん）

#### 1. セッションを開始

- VSCode下部の「**Live Share**」ボタンをクリック
- または `Ctrl+Shift+P` → 「Live Share: Start Collaboration Session」と入力

#### 2. 招待リンクが自動生成される

```
例: https://prod.liveshare.vsengsaas.visualstudio.com/join?B1A2C3D4E5...
```

- **自動的にクリップボードにコピーされます**
- 画面右下に通知が表示されます

#### 3. リンクを送信

- LINE、メール、Slack、Discord、何でもOK！
- 相手（あなた）に送信

---

### 👥 ゲスト側（あなた）

#### 1. 招待リンクを受け取る

詩織さんから送られてきたリンクをコピー

#### 2. セッションに参加

**方法A: リンクをクリック（最も簡単）**
- リンクをブラウザで開く
- 自動的にVSCodeが起動して参加

**方法B: VSCode内から**
- `Ctrl+Shift+P`
- 「Live Share: Join Collaboration Session」と入力
- リンクを貼り付けて Enter

#### 3. 接続完了！

- 詩織さんと同じファイルが表示されます
- お互いのカーソル位置が色付きで見えます
- **リアルタイム共同編集スタート！**

---

## ステップ3: 一緒に開発

### ✅ できること

#### 1. リアルタイムコード編集

```
詩織さん: app/routes/materials.py を編集
あなた: app/templates/materials.html を編集
→ 同時に違うファイルを編集可能！
```

- お互いのカーソル位置が見える
- 誰がどこを編集しているか一目瞭然
- コンフリクトの心配なし

#### 2. ターミナル共有

**ホスト（詩織さん）が共有:**
1. Live Shareビュー（左サイドバー）を開く
2. 「Shared Terminals」→「Share Terminal」
3. Read/Write（読み書き可能）または Read-Only（読み取り専用）を選択

**ゲスト（あなた）:**
- 共有されたターミナルでコマンド実行可能
- Flaskアプリの起動状況を一緒に確認

#### 3. サーバー共有（重要！）

**ホスト（詩織さん）:**
```bash
# Flaskアプリを起動
python run.py

# VSCodeのLive Shareビュー
→ Shared Servers
→ Share Server
→ ポート番号: 5000 を入力
```

**ゲスト（あなた）:**
- 自動的に `localhost:5000` で詩織さんのサーバーにアクセス可能
- ブラウザで開いて動作確認

#### 4. デバッグ共有

- ブレークポイントを一緒に設定
- ステップ実行を共有
- 変数の値を一緒に確認

#### 5. フォロー機能

```
詩織さんが見ているファイル・場所にジャンプ:
→ Live Shareビュー
→ Participants
→ 詩織さんの名前をクリック
→ 「Follow Participant」
```

---

## 📋 実践例: 新機能を一緒に開発

### シナリオ: 材料管理画面に新しいフィルター機能を追加

#### タイムライン

**0:00 - セッション開始**
```
詩織さん: Live Shareセッション開始
詩織さん: 招待リンクをあなたに送信
あなた: リンクをクリックして参加
```

**0:02 - 環境準備**
```
詩織さん: python run.py でFlaskアプリ起動
詩織さん: ターミナル共有（Read/Write）
詩織さん: サーバー共有（ポート5000）
あなた: ブラウザでlocalhost:5000を開く
```

**0:05 - 役割分担**
```
詩織さん: バックエンド（app/routes/materials.py）を担当
あなた: フロントエンド（app/templates/materials.html）を担当
```

**0:10 - 共同開発**
```python
# 詩織さんが編集中: app/routes/materials.py
@app.route('/materials')
def materials():
    category = request.args.get('category')  # フィルター追加
    if category:
        materials = Material.query.filter_by(category=category).all()
    else:
        materials = Material.query.all()
    return render_template('materials.html', materials=materials)
```

```html
<!-- あなたが同時に編集中: app/templates/materials.html -->
<select id="category-filter">
  <option value="">すべて</option>
  <option value="粉類">粉類</option>
  <option value="乳製品">乳製品</option>
</select>
```

**0:20 - 動作確認**
```
詩織さん: 保存（Ctrl+S）
あなた: ブラウザをリロード
→ リアルタイムで動作確認！
```

**0:25 - デバッグ**
```
詩織さん: ブレークポイント設定
あなた: 一緒にステップ実行で確認
→ 問題箇所を特定
→ その場で修正
```

**0:30 - 完成！**
```
詩織さん: セッション終了
詩織さん: git add . && git commit && git push
```

---

## 💡 便利な機能

### 音声通話（オプション）

Live Share Extension Packに含まれる音声通話機能:
```
Live Shareビュー → Start audio call
```

### チャット機能

```
Live Shareビュー → Session Chat
→ テキストでやり取り
```

### 複数人での参加

- 2人以上でも参加可能
- チーム全員で一緒に開発

---

## 🔧 トラブルシューティング

### Q: Live Shareボタンが見つからない

```bash
# 拡張機能を再インストール
code --install-extension MS-vsliveshare.vsliveshare --force

# VSCodeを再起動
```

### Q: 接続できない・リンクが開けない

1. **両者ともサインイン済みか確認**
   - VSCode下部の「Live Share」ボタンの状態を確認

2. **ファイアウォール確認**
   - Live ShareはHTTPS（ポート443）を使用
   - 通常の環境では問題なし

3. **VSCodeを最新版に更新**

### Q: サーバー（localhost:5000）が見えない

**ホスト側:**
```
1. Live Shareビューを開く
2. Shared Servers セクション
3. Share Server をクリック
4. ポート番号 5000 を入力
5. 「Share」をクリック
```

### Q: ターミナルが共有されない

**ホスト側:**
```
1. Live Shareビューを開く
2. Shared Terminals セクション
3. Share Terminal をクリック
4. Read/Write を選択
```

### Q: 相手のカーソルが見えない

- ファイルを開き直す
- Live Shareセッションを再接続

---

## ⚠️ 注意事項

### セッション終了後

- **変更はホスト側にのみ保存されます**
- ゲスト側には変更が残りません
- ホスト（詩織さん）がコミット・プッシュ

### ファイルの保存

- ホストとゲスト、どちらも保存可能
- ホストのファイルシステムに反映される

### アクセス権限

ホストは以下を制御可能:
- ファイルの読み取り専用/編集可能
- ターミナルのRead-only/Read-Write
- デバッグセッションの共有

---

## 🎯 よくある使い方パターン

### パターン1: ペアプログラミング

```
詩織さん: 設計やロジックを説明しながらコードを書く
あなた: 一緒に見ながら提案・質問
→ 役割を交代することも可能
```

### パターン2: コードレビュー

```
詩織さん: 書いたコードを共有
あなた: Live Shareで参加してレビュー
→ その場で修正・改善
```

### パターン3: デバッグセッション

```
問題のあるコードをLive Shareで共有
→ 一緒にデバッグ実行
→ 原因特定
→ その場で修正
```

### パターン4: 教え合い

```
詩織さん: 新しい技術や機能を実装
あなた: 画面共有で学習
→ リアルタイムで質問・実践
```

---

## ✅ クイックリファレンス

### ホスト（詩織さん）の操作

```bash
# 1. セッション開始
VSCode下部「Live Share」をクリック

# 2. リンクを送信
自動コピーされたリンクを相手に送信

# 3. ターミナル共有（オプション）
Live Shareビュー → Share Terminal

# 4. サーバー共有（オプション）
Live Shareビュー → Share Server → 5000

# 5. セッション終了
「Live Share」→「Stop Collaboration Session」
```

### ゲスト（あなた）の操作

```bash
# 1. セッション参加
受け取ったリンクをクリック

# 2. ファイル編集
通常通り編集可能

# 3. 詩織さんをフォロー（オプション）
Live Shareビュー → Participants → Follow

# 4. セッション退出
「Live Share」→「Leave Collaboration Session」
```

---

## 📞 今すぐ始める手順

### ステップ1: 両者が準備

```bash
# 1. Live Share拡張機能をインストール
code --install-extension MS-vsliveshare.vsliveshare

# 2. VSCodeでサインイン
下部の「Live Share」ボタン → サインイン
```

### ステップ2: 詩織さんがセッション開始

```bash
# 1. Bakery_systemをVSCodeで開く
cd ~/Bakery_system
code .

# 2. Live Share開始
下部の「Live Share」ボタンをクリック

# 3. リンクを送信
自動コピーされたリンクを送信
```

### ステップ3: あなたが参加

```bash
# リンクをクリックするだけ！
# または
# Ctrl+Shift+P → "Live Share: Join" → リンク貼り付け
```

### ステップ4: 一緒に開発開始！

---

これで準備完了です！詩織さんと一緒に楽しく開発してください！

質問があれば、GitHubのIssuesまたはこのチャットで聞いてください。
