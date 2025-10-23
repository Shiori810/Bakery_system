# 開発ガイド

## リポジトリのクローンと初期セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/SATOET/bakery-cost-calculator-.git
cd bakery-cost-calculator-
```

### 2. 仮想環境の作成と有効化

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存パッケージのインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install "pydantic[email]"
```

### 4. 環境変数の設定

`.env.example`を`.env`にコピー:
```bash
cp .env.example .env
```

`.env`ファイルを編集して必要な設定を行います。

### 5. アプリケーションの起動

```bash
python -m uvicorn app.main:app --reload
```

ブラウザで http://localhost:8000 にアクセス

## 共同開発のワークフロー

### ブランチ戦略

- `main` - 本番環境用の安定版ブランチ
- `develop` - 開発用のメインブランチ
- `feature/機能名` - 新機能開発用ブランチ
- `bugfix/バグ名` - バグ修正用ブランチ
- `hotfix/修正名` - 緊急修正用ブランチ

### 開発手順

#### 1. 最新のコードを取得

```bash
git checkout main
git pull origin main
```

#### 2. 新しいブランチを作成

```bash
# 機能開発の場合
git checkout -b feature/新機能名

# バグ修正の場合
git checkout -b bugfix/バグ名
```

#### 3. コードを編集して変更をコミット

```bash
git add .
git commit -m "機能追加: ○○機能を実装"
```

#### 4. GitHubにプッシュ

```bash
git push origin feature/新機能名
```

#### 5. Pull Request（PR）を作成

1. GitHubのリポジトリページにアクセス
2. "Compare & pull request" ボタンをクリック
3. 変更内容を説明
4. レビュワーを指定
5. "Create pull request" をクリック

#### 6. コードレビュー

- レビュワーがコードを確認
- 必要に応じて修正
- 承認されたらマージ

#### 7. ブランチの削除

マージ後、不要になったブランチを削除:
```bash
git checkout main
git pull origin main
git branch -d feature/新機能名
```

## コミットメッセージの規約

わかりやすいコミットメッセージを心がけましょう:

- `機能追加: ○○機能を実装`
- `修正: ○○のバグを修正`
- `改善: ○○のパフォーマンスを改善`
- `リファクタリング: ○○を整理`
- `ドキュメント: README を更新`
- `テスト: ○○のテストを追加`

## コードスタイル

### Python コーディング規約

- PEP 8 に従う
- 関数やクラスにはdocstringを記述
- 型ヒントを使用

### フォーマッター

推奨ツール:
```bash
pip install black flake8 isort
```

使用方法:
```bash
# コードフォーマット
black app/

# リンター
flake8 app/

# インポート整理
isort app/
```

## テスト

### テストの実行

```bash
pytest tests/
```

### 新しいテストの追加

`tests/` ディレクトリに追加してください。

## トラブルシューティング

### 依存関係の問題

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### データベースのリセット

```bash
rm bakery.db
# アプリケーションを起動すると自動的に再作成されます
```

### ポートが使用中

別のポートで起動:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

## 連絡先

質問や問題がある場合は、GitHubのIssueを作成してください。
