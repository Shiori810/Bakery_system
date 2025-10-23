# VSCodeでの共同作業ガイド

VSCodeを使って複数人で効率的に開発する方法を説明します。

## 方法1: Live Share（リアルタイム共同編集）

### Live Shareとは？

VSCode Live Shareは、リアルタイムで複数人が同じコードを編集できる機能です。
- リアルタイムでコードを共同編集
- デバッグセッションの共有
- ターミナルの共有
- ローカルサーバーの共有

### セットアップ手順

#### 1. Live Share拡張機能のインストール

1. VSCodeを開く
2. 左サイドバーの拡張機能アイコンをクリック（または `Ctrl+Shift+X`）
3. "Live Share" を検索
4. **Live Share Extension Pack** をインストール

または、コマンドラインから：
```bash
code --install-extension MS-vsliveshare.vsliveshare
```

#### 2. Microsoftアカウントでサインイン

1. VSCodeの下部ステータスバーの「Live Share」をクリック
2. GitHubまたはMicrosoftアカウントでサインイン

### 使い方

#### ホスト（共有する側）

1. **共有セッションを開始**
   - ステータスバーの「Live Share」をクリック
   - または `Ctrl+Shift+P` → "Live Share: Start Collaboration Session"

2. **招待リンクが生成される**
   - 自動的にクリップボードにコピーされます
   - このリンクを共同作業者に送信

3. **参加者を管理**
   - 読み取り専用 or 編集可能を設定
   - 特定のファイル/フォルダへのアクセス制限

#### ゲスト（参加する側）

1. **セッションに参加**
   - ホストから受け取ったリンクをクリック
   - または `Ctrl+Shift+P` → "Live Share: Join Collaboration Session"
   - リンクを貼り付け

2. **共同編集開始**
   - ホストと同じファイルが開きます
   - お互いのカーソル位置が表示されます

### Live Shareの便利機能

#### ターミナル共有

```
Live Share ビュー → Share Terminal → Read/Write or Read-Only
```

ホストのターミナルを共有して、ゲストもコマンドを実行できます。

#### サーバー共有

ローカルで動いているサーバー（例：http://localhost:8000）をゲストも閲覧可能：
```
Live Share ビュー → Share Server → ポート番号入力（例：8000）
```

#### 音声通話

Live Share Extension Pack には音声通話機能も含まれています。

## 方法2: GitHub統合（非同期の共同作業）

### GitHubアカウントとの連携

#### 1. GitHub拡張機能のインストール

推奨拡張機能：
- **GitHub Pull Requests and Issues**
- **GitLens**
- **Git Graph**

```bash
code --install-extension GitHub.vscode-pull-request-github
code --install-extension eamodio.gitlens
code --install-extension mhutchie.git-graph
```

#### 2. GitHubにサインイン

1. VSCodeの左下のアカウントアイコンをクリック
2. "Sign in to Sync Settings" → GitHubを選択
3. ブラウザで認証

### GitHub機能の活用

#### Pull Requestの作成・レビュー

1. **ソースコントロールビュー**（`Ctrl+Shift+G`）
2. 変更をコミット
3. "Create Pull Request" ボタン
4. タイトルと説明を入力して作成

#### Issueの管理

1. 左サイドバーの「GitHub」アイコン
2. Issues セクションで確認・作成・編集

#### コードレビュー

1. Pull Requests セクションを開く
2. レビューしたいPRを選択
3. インラインでコメント追加
4. Approve/Request Changes

## 方法3: Dev Containers（環境の統一）

### Dev Containersとは？

Dockerコンテナ内で開発環境を統一し、全員が同じ環境で作業できます。

### セットアップ

#### 1. 必要なツール

- Docker Desktop
- VSCode拡張機能: **Dev Containers**

```bash
code --install-extension ms-vscode-remote.remote-containers
```

#### 2. 設定ファイルの作成

`.devcontainer/devcontainer.json` を作成：

```json
{
  "name": "Bakery Cost Calculator Dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.14",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter"
      ]
    }
  },
  "postCreateCommand": "pip install -r requirements.txt && pip install 'pydantic[email]'",
  "forwardPorts": [8000],
  "portsAttributes": {
    "8000": {
      "label": "FastAPI Server"
    }
  }
}
```

#### 3. コンテナで開く

1. `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"
2. 初回は環境構築に時間がかかります
3. 全員が同じ環境で開発可能

## 推奨: プロジェクト設定の共有

### ワークスペース設定

`.vscode/settings.json` を作成（プロジェクト全体で共有）：

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true
  }
}
```

### 推奨拡張機能

`.vscode/extensions.json` を作成：

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-vsliveshare.vsliveshare",
    "eamodio.gitlens",
    "github.vscode-pull-request-github",
    "mhutchie.git-graph"
  ]
}
```

## 開発ワークフローのベストプラクティス

### 日常的な作業フロー

```bash
# 1. 最新コードを取得
git checkout main
git pull origin main

# 2. 新しいブランチで作業
git checkout -b feature/your-feature

# 3. VSCodeで開発
code .

# 4. 定期的にコミット
# Git Source Control ビューで変更を確認
# ステージング → コミット

# 5. プッシュしてPR作成
# Source Control ビュー → "..." → "Push"
# GitHub拡張機能からPR作成
```

### チーム開発のヒント

#### 1. コンフリクトを避ける

- 作業前に必ず `git pull`
- 小さな単位でコミット・プッシュ
- 長期間ブランチを放置しない

#### 2. コミュニケーション

- Live Shareで画面共有しながらペアプログラミング
- PR でコメントを活用
- Issue で質問・提案

#### 3. コードの品質

- 保存時に自動フォーマット（Black）
- コミット前にリンター実行（Flake8）
- PR前にテスト実行

## トラブルシューティング

### Live Shareが接続できない

```bash
# ファイアウォールを確認
# ポート設定を確認
# VSCodeとLive Shareを最新版に更新
```

### Gitの認証エラー

```bash
# 認証情報を再設定
git config --global credential.helper wincred

# VSCodeで再サインイン
# アカウントアイコン → Sign out → Sign in
```

### Python環境が認識されない

```bash
# VSCodeでインタープリターを選択
# Ctrl+Shift+P → "Python: Select Interpreter"
# venv/Scripts/python.exe を選択
```

## まとめ

### リアルタイム共同作業が必要な場合
→ **Live Share** を使用

### 通常のチーム開発の場合
→ **GitHub統合** + ブランチ戦略

### 環境の統一が重要な場合
→ **Dev Containers**

---

質問や問題がある場合は、GitHubのIssueを作成してください。
