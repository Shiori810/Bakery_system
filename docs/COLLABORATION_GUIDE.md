# VSCodeでの共同作業ガイド

このガイドでは、Bakery_systemプロジェクトでVSCodeを使って共同作業する方法を説明します。

## クイックスタート

### 1. リポジトリをクローン

```bash
git clone https://github.com/Shiori810/Bakery_system.git
cd Bakery_system
```

### 2. VSCodeで開く

```bash
code .
```

VSCodeを開くと、自動的に推奨拡張機能のインストールを提案します。

### 3. 環境セットアップ

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化（Windows）
venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
# .envファイルを編集
```

### 4. アプリケーションを起動

```bash
python run.py
```

ブラウザで http://localhost:5000 にアクセス

## 共同作業の方法

### 方法1: Live Share（リアルタイム共同編集）

**最もおすすめ！ペアプログラミングに最適**

#### セットアップ

1. VSCodeで拡張機能「Live Share」をインストール
   - `Ctrl+Shift+X` → "Live Share" を検索 → インストール

2. VSCode下部ステータスバーの「Live Share」をクリック

3. GitHubまたはMicrosoftアカウントでサインイン

#### 使い方

**ホスト（共有する側）:**
1. ステータスバーの「Live Share」をクリック
2. 「Start collaboration session」を選択
3. 招待リンクが自動的にクリップボードにコピーされる
4. リンクを共同作業者に送信

**ゲスト（参加する側）:**
1. 受け取ったリンクをクリック、またはVSCodeで `Ctrl+Shift+P` → "Live Share: Join"
2. リンクを貼り付け
3. 共同編集開始！

#### Live Shareでできること

- **リアルタイムコード編集**: お互いのカーソル位置が見える
- **ターミナル共有**: コマンドを一緒に実行
- **サーバー共有**: ホストのlocalhost:5000をゲストも閲覧可能
- **デバッグ共有**: 一緒にデバッグセッションを実行
- **音声通話**: 拡張機能に含まれる（オプション）

### 方法2: GitHub Pull Request ワークフロー

**通常のチーム開発に最適**

#### 基本的な流れ

```bash
# 1. 最新のコードを取得
git checkout main
git pull origin main

# 2. 新しいブランチを作成
git checkout -b feature/your-feature-name

# 3. 開発・コミット
# VSCodeのSource Controlビュー (Ctrl+Shift+G) を使用
git add .
git commit -m "機能追加: ○○を実装"

# 4. GitHubにプッシュ
git push origin feature/your-feature-name

# 5. Pull Requestを作成
# GitHubのページで「Compare & pull request」をクリック
```

#### VSCode内でのGit操作

1. **Source Controlビュー** (`Ctrl+Shift+G`)
   - 変更ファイルの確認
   - ステージング
   - コミット

2. **GitHub拡張機能**（推奨）
   - Pull Requestの作成・レビュー
   - Issueの管理
   - インラインコメント

### 方法3: Dev Containers（環境統一）

**全員が同じ環境で開発したい場合**

Docker環境で開発環境を完全に統一できます。

## VSCode設定の説明

このプロジェクトには、チーム全員で共有するVSCode設定が含まれています：

### `.vscode/settings.json`
- Python環境の自動認識
- Black/Flake8による自動フォーマット
- 保存時の自動整形
- Jinja2テンプレートのサポート

### `.vscode/extensions.json`
推奨拡張機能:
- Python (必須)
- Live Share (リアルタイム共同編集)
- GitLens (Git履歴可視化)
- Jinja (テンプレートサポート)

### `.vscode/launch.json`
デバッグ設定:
- **Flask: Debug** - Flaskアプリのデバッグ実行
- **Python: Current File** - 個別ファイルの実行

## 開発ワークフローのベストプラクティス

### コミットの頻度

- 小さな単位で頻繁にコミット
- 1つのコミットで1つの変更
- わかりやすいコミットメッセージ

### コミットメッセージの例

```
機能追加: 商品カテゴリーフィルタを追加
修正: ラベル印刷時の日付フォーマットを修正
改善: 原価計算のパフォーマンスを最適化
リファクタリング: ユーザー認証ロジックを整理
ドキュメント: READMEにセットアップ手順を追記
```

### コードレビュー

Pull Requestを作成したら:
1. 変更内容を明確に説明
2. スクリーンショットを添付（UI変更の場合）
3. テスト方法を記載
4. レビュワーを指定

## トラブルシューティング

### Live Shareに接続できない

```bash
# ファイアウォール設定を確認
# VSCodeとLive Share拡張機能を最新版に更新
code --install-extension MS-vsliveshare.vsliveshare --force
```

### Python環境が認識されない

1. `Ctrl+Shift+P` → "Python: Select Interpreter"
2. `venv/Scripts/python.exe` を選択

### Gitの認証エラー

```bash
# 認証情報を再設定
git config --global credential.helper wincred

# VSCodeで再サインイン
# 左下のアカウントアイコン → Sign out → Sign in
```

## よくある質問

### Q: Live Shareとプルリクエスト、どちらを使うべき？

**Live Share**: 
- ペアプログラミング
- リアルタイムで相談しながら開発
- 新機能の設計段階

**Pull Request**: 
- レビューが必要な変更
- 非同期で作業
- コード品質の維持

両方を組み合わせることも可能です！

### Q: 他の人の変更とコンフリクトしたら？

```bash
# mainブランチの最新を取得
git checkout main
git pull origin main

# 自分のブランチにマージ
git checkout your-branch
git merge main

# コンフリクトを解決（VSCodeのマージエディタが便利）
# 解決後:
git add .
git commit -m "マージコンフリクトを解決"
git push origin your-branch
```

## まとめ

- **リアルタイム共同作業** → Live Share
- **通常のチーム開発** → GitHub + Pull Request
- **環境の統一** → Dev Containers

すべての方法をサポートしているので、状況に応じて使い分けましょう！

---

質問や問題があれば、GitHubのIssuesで質問してください。
