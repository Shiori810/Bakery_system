# Renderへのデプロイ完全ガイド

## 概要
このドキュメントは、Bakery_systemアプリケーションをRenderにデプロイする詳細な手順と、実際に発生した問題とその解決方法を記録したものです。

## デプロイ日
2025年10月27日

## 実際のデプロイ手順

### 1. GitHubへのプッシュ

#### 1.1 変更内容のステージング
```bash
cd Bakery_system
git add .
git status  # 変更内容を確認
```

**コミットされた内容:**
- 原価計算の単位変換修正（kg↔g, L↔ml対応）
- 販売価格の手動設定機能追加
- A-ONE製品対応ラベル印刷（7種類のプリセット）
- カスタムラベルサイズ設定機能
- パスワードリセット機能（ログインID確認方式）
- ログインID復旧機能（店舗名検索）
- テンプレート表示エラーの修正
- 機能ドキュメント追加（3件）

#### 1.2 コミットとプッシュ
```bash
git commit -m "Add authentication recovery and label customization features

- 原価計算の単位変換修正（kg↔g, L↔ml対応）
- 販売価格の手動設定機能追加
- A-ONE製品対応ラベル印刷（7種類のプリセット）
- カスタムラベルサイズ設定機能
- パスワードリセット機能（ログインID確認方式）
- ログインID復旧機能（店舗名検索）
- テンプレート表示エラーの修正
- 機能ドキュメント追加（3件）

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

#### 1.3 requirements.txtの更新
本番環境用のパッケージを有効化：
```bash
# requirements.txtを編集
# gunicorn==21.2.0 → gunicorn==21.2.0（コメント解除）
# psycopg2-binary==2.9.9 → psycopg2-binary==2.9.9（コメント解除）

git add requirements.txt
git commit -m "Enable gunicorn and psycopg2-binary for production deployment"
git push origin main
```

### 2. PostgreSQLデータベースの作成

#### 2.1 Renderダッシュボードでデータベース作成
1. https://render.com にログイン
2. **New +** → **PostgreSQL** を選択
3. 設定：
   - **Name**: `bakery-db`
   - **Database**: `bakery_i62w`（自動生成）
   - **User**: `bakery_i62w_user`（自動生成）
   - **Region**: `Singapore`
   - **PostgreSQL Version**: 16（最新版）
   - **Datastore Plan**: **Free**

#### 2.2 データベースURL取得
作成後、以下のURLを取得：

**Internal Database URL（短縮版 - 動作しない）:**
```
postgresql://bakery_i62w_user:eUZLhUG9BPMb12BHoxHz22Gknu3qoqSK@dpg-d3vfqv3ipnbc739kbnm0-a/bakery_i62w
```

**External Database URL（完全版 - 使用可能）:**
```
postgresql://bakery_i62w_user:eUZLhUG9BPMb12BHoxHz22Gknu3qoqSK@dpg-d3vfqv3ipnbc739kbnm0-a.singapore-postgres.render.com/bakery_i62w
```

**重要:** Internal URLが短縮形式の場合、`.singapore-postgres.render.com` などの完全なホスト名を含むExternal URLを使用する必要があります。

### 3. Web Serviceの作成

#### 3.1 新しいWeb Serviceを作成
1. Renderダッシュボードで **New +** → **Web Service** を選択
2. GitHubリポジトリ `Shiori810/Bakery_system` を接続

#### 3.2 基本設定
- **Name**: `Bakery_system`
- **Region**: `Singapore`（データベースと同じリージョン推奨）
- **Branch**: `main`
- **Root Directory**: 空欄（リポジトリのルートが`Bakery_system`フォルダ）
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn run:app`（初期設定 - 後で変更）
- **Instance Type**: `Free`

### 4. 環境変数の設定

#### 4.1 SECRET_KEYの生成
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

生成されたキー:
```
8542f3d9ae937685a67db32b6802704bb402e71ec896ace38a37f4aa4bbfa7e2
```

#### 4.2 環境変数の追加
Renderの環境変数設定で以下を追加：

**環境変数1:**
- KEY: `SECRET_KEY`
- VALUE: `8542f3d9ae937685a67db32b6802704bb402e71ec896ace38a37f4aa4bbfa7e2`

**環境変数2:**
- KEY: `DATABASE_URL`
- VALUE: `postgresql://bakery_i62w_user:eUZLhUG9BPMb12BHoxHz22Gknu3qoqSK@dpg-d3vfqv3ipnbc739kbnm0-a.singapore-postgres.render.com/bakery_i62w`

### 5. 発生した問題と解決方法

#### 問題1: Gunicornの起動エラー
**エラーメッセージ:**
```
gunicorn errors.AppImportError: Failed to find attribute 'app' in 'app'.
```

**原因:**
Start Commandが `gunicorn run:app` だけでは不十分で、ポート指定とワーカー数が必要。

**解決方法:**
Settings → Start Command を以下に変更：
```bash
gunicorn -w 4 -b 0.0.0.0:$PORT run:app
```

**パラメータ説明:**
- `-w 4`: ワーカープロセス数を4に設定
- `-b 0.0.0.0:$PORT`: すべてのインターフェースでRenderが指定するポートをバインド
- `run:app`: run.pyモジュールのappオブジェクトを起動

#### 問題2: PostgreSQL接続エラー
**エラーメッセージ:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not translate host name "dpg-d3vfqv3ipnbc739kbnm0-a" to address: Name or service not known
```

**原因:**
Internal Database URLが短縮形式（`@dpg-d3vfqv3ipnbc739kbnm0-a/`）で、完全なホスト名が含まれていない。

**解決方法:**
External Database URLを使用：
```
postgresql://bakery_i62w_user:eUZLhUG9BPMb12BHoxHz22Gknu3qoqSK@dpg-d3vfqv3ipnbc739kbnm0-a.singapore-postgres.render.com/bakery_i62w
```

完全なホスト名（`.singapore-postgres.render.com`）が含まれているため、DNSで解決可能。

**注意:** Renderの無料PostgreSQLでは、Internal URLが短縮形式のみの場合があります。その場合は必ずExternal URLを使用してください。

### 6. デプロイ成功

#### 6.1 最終的な設定

**Start Command:**
```bash
gunicorn -w 4 -b 0.0.0.0:$PORT run:app
```

**環境変数:**
```
SECRET_KEY=8542f3d9ae937685a67db32b6802704bb402e71ec896ace38a37f4aa4bbfa7e2
DATABASE_URL=postgresql://bakery_i62w_user:eUZLhUG9BPMb12BHoxHz22Gknu3qoqSK@dpg-d3vfqv3ipnbc739kbnm0-a.singapore-postgres.render.com/bakery_i62w
```

#### 6.2 デプロイ完了
- **公開URL**: https://bakery-system.onrender.com
- **ステータス**: Live（稼働中）
- **デプロイ時刻**: 2025年10月27日 14:53（日本時間）

#### 6.3 デプロイログの確認
```
Successfully installed Flask-3.0.0 Flask-Login-0.6.3 Flask-SQLAlchemy-3.1.1
Flask-WTF-1.2.1 WTForms-3.1.1 bcrypt-4.1.2 blinker-1.8.0 click-8.3.0
dnspython-2.0.0 email-validator-2.1.0 greenlet-3.1.1 gunicorn-21.2.0
idna-3.11 itsdangerous-2.1.0 pillow-12.0.0 psycopg2-binary-2.9.9
python-dotenv-1.0.0 reportlab-4.0.7 sqlalchemy-2.0.44 werkzeug-3.1.3

[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:10000
[INFO] Using worker: sync
[INFO] Booted worker with pid: 52
[INFO] Booted worker with pid: 53
[INFO] Booted worker with pid: 54
[INFO] Booted worker with pid: 55

==> Your service is live 🎉
```

## データベースについて

### ローカル環境と本番環境の違い

**ローカル環境:**
- データベース: SQLite（`instance/bakery.db`）
- URL: http://localhost:5000
- データ: ローカルPC上に保存

**本番環境（Render）:**
- データベース: PostgreSQL（`bakery_i62w`）
- URL: https://bakery-system.onrender.com
- データ: Renderのクラウド上に保存

### 重要な注意事項
ローカル環境と本番環境のデータベースは完全に別のものです。ローカルで作成したアカウントやデータは本番環境には存在しません。

本番環境では新しくアカウントを作成する必要があります。

## 自動デプロイ

GitHubの`main`ブランチにプッシュすると、Renderが自動的に：
1. 変更を検出
2. ビルドを実行
3. デプロイ

デプロイ時間: 約3-5分

## カスタムドメイン設定（オプション）

### 前提条件
- Renderの有料プラン（Starter以上、$7/月〜）が必要
- 独自ドメインを所有していること

### 設定手順

#### 1. Renderでカスタムドメインを追加
1. Bakery_system Web Service → **Settings**
2. **Custom Domain** セクションで **Add Custom Domain**
3. ドメイン名を入力（例: `bakery.etsu-dev.com`）
4. Renderが表示するCNAME値をメモ

#### 2. DNSプロバイダーで設定（お名前.comの例）
1. お名前.com Naviにログイン
2. ドメイン設定 → DNS設定
3. CNAMEレコードを追加または編集：
   - **Type**: CNAME
   - **Host**: `bakery`
   - **Value**: `bakery-system.onrender.com`
   - **TTL**: 3600

#### 3. SSL証明書の自動発行
Renderが自動的に：
- Let's Encrypt SSL証明書を発行
- HTTPSを有効化
- DNS伝播完了を待機（15分〜数時間）

#### 4. アクセス確認
DNS伝播後、カスタムドメインでアクセス可能：
- https://bakery.etsu-dev.com/

### カスタムドメイン使用時の注意
- 無料プランでは利用不可
- Starter プラン（$7/月）以上が必要
- 既存の`.onrender.com`ドメインも引き続き使用可能

## 監視とメンテナンス

### ログの確認
Renderダッシュボード → **Logs** で以下を確認可能：
- アプリケーションログ
- エラーログ
- アクセスログ

### メトリクスの確認
Renderダッシュボード → **Metrics** で以下を確認可能：
- CPU使用率
- メモリ使用量
- レスポンスタイム
- リクエスト数

### 無料プランの制限
- **15分間アクセスなし**: スリープモードに移行
- **初回アクセス**: 起動まで30秒〜1分かかる
- **月間稼働時間**: 750時間まで無料（1ヶ月分以上）

## トラブルシューティング

### デプロイが失敗する

**ビルドエラー:**
```
ERROR: Could not find a version that satisfies the requirement
```
→ `requirements.txt`のパッケージバージョンを確認

**起動エラー:**
```
AppImportError: Failed to find attribute 'app'
```
→ Start Commandが正しいか確認（`gunicorn -w 4 -b 0.0.0.0:$PORT run:app`）

### データベース接続エラー

**ホスト名解決エラー:**
```
could not translate host name to address
```
→ DATABASE_URLに完全なホスト名（`.render.com`で終わる）が含まれているか確認
→ Internal URLではなくExternal URLを使用

**認証エラー:**
```
password authentication failed
```
→ DATABASE_URLのユーザー名とパスワードが正しいか確認

### アプリケーションが遅い

**無料プランのスリープ:**
- 15分間アクセスがないとスリープ
- 初回アクセス時に30秒〜1分の起動時間

**解決策:**
- 有料プラン（Starter以上）にアップグレード
- または、定期的にアクセスしてスリープを防ぐ

## バックアップ

### データベースバックアップ
Renderの無料PostgreSQLプランでは自動バックアップがありません。

**手動バックアップ方法:**
1. Renderダッシュボード → bakery-db → **Shell**
2. `pg_dump`コマンドでダンプを取得
3. ローカルに保存

**推奨頻度:**
- 重要なデータがある場合: 週1回以上
- 本番運用中: 毎日

## セキュリティ

### 本番環境でのベストプラクティス

1. **SECRET_KEYの管理**
   - 絶対にGitHubにコミットしない
   - 環境変数のみで管理
   - 定期的に変更（推奨: 3ヶ月ごと）

2. **データベース認証情報**
   - 環境変数のみで管理
   - External URLは外部に公開しない

3. **HTTPS**
   - Renderは自動的にHTTPSを有効化
   - HTTPからHTTPSへの自動リダイレクト

4. **依存パッケージの更新**
   - 定期的に`pip list --outdated`で確認
   - セキュリティアップデートは優先的に適用

## 更新のデプロイ手順

### 通常のアップデート
```bash
# 1. コードを修正
# 2. ローカルでテスト
cd Bakery_system
python run.py  # ローカルで動作確認

# 3. Gitにコミット
git add .
git commit -m "Update: 変更内容の説明"
git push origin main

# 4. Renderが自動的にデプロイ（3-5分）
```

### 環境変数の変更
1. Renderダッシュボード → **Environment**
2. 変更したい変数を編集
3. **Save Changes**
4. 自動的に再デプロイ

### データベーススキーマの変更
1. `app/models.py`を修正
2. Gitにコミット＆プッシュ
3. デプロイ後、`db.create_all()`が自動実行される

**注意:** 既存のカラムの削除や型変更は手動マイグレーションが必要

## まとめ

### 成功した設定
- **GitHubリポジトリ**: `Shiori810/Bakery_system`
- **公開URL**: https://bakery-system.onrender.com
- **データベース**: PostgreSQL（Singapore、無料プラン）
- **Web Service**: Python 3 + Gunicorn（無料プラン）

### 実装されている機能
- ✓ 原価計算（単位変換対応）
- ✓ 販売価格手動設定
- ✓ A-ONEラベル印刷
- ✓ カスタムラベルサイズ
- ✓ パスワードリセット
- ✓ ログインID復旧
- ✓ 店舗管理
- ✓ 材料管理
- ✓ レシピ管理

### 次のステップ
1. 本番環境で新規アカウント作成
2. 動作確認
3. 必要に応じてカスタムドメイン設定（有料プラン）
4. データのバックアップ体制構築
5. 監視とメンテナンス

---
作成日: 2025年10月27日
最終更新: 2025年10月27日
デプロイURL: https://bakery-system.onrender.com
