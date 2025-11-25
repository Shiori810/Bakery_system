# Renderへのデプロイ手順

## 事前準備

このアプリケーションはRenderで無料デプロイできます。

## デプロイ手順

### 1. Renderアカウントの作成

1. https://render.com/ にアクセス
2. `Get Started for Free` をクリック
3. GitHubアカウントでサインアップ

### 2. 新しいWebサービスを作成

1. Renderダッシュボードで `New +` をクリック
2. `Web Service` を選択
3. GitHubリポジトリを接続
   - `Connect account` をクリック
   - リポジトリ `Shiori810/Bakery_system` を選択
   - `Connect` をクリック

### 3. サービスの設定

以下の設定を入力：

- **Name**: `Bakery_system`（または任意の名前）
- **Region**: `Singapore` または最寄りのリージョン（データベースと同じリージョン推奨）
- **Branch**: `main`
- **Root Directory**: 空欄（デフォルト）
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT run:app`（重要: ポート指定が必須）

### 4. プランを選択

- **Instance Type**: `Free`（無料プラン）

### 5. 環境変数を設定

`Environment` セクションで以下を追加：

```
SECRET_KEY = [自動生成または任意のランダム文字列]
DATABASE_URL = [PostgreSQLデータベースのURL - 後で設定]
```

SECRET_KEYは以下のコマンドで生成できます：
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. PostgreSQLデータベースを作成

1. Renderダッシュボードで `New +` → `PostgreSQL` を選択
2. 設定：
   - **Name**: `bakery-db`
   - **Database**: `bakery`
   - **User**: `bakery_user`
   - **Region**: Webサービスと同じリージョン
   - **Plan**: `Free`

3. `Create Database` をクリック

4. データベース詳細ページで `External Database URL` をコピー
   - **重要**: Internal URLが短縮形式（`@dpg-xxx-a/`）の場合、External URLを使用
   - External URLは完全なホスト名（`.singapore-postgres.render.com`など）を含む
   - 目のアイコン（👁️）をクリックして完全なURLを表示

5. Webサービスの環境変数に戻って：
   - `DATABASE_URL` = コピーした**External** Database URL

### 7. デプロイを実行

1. `Create Web Service` をクリック
2. デプロイが自動的に開始されます
3. ログを確認（ビルドとデプロイの進行状況）

### 8. デプロイ完了

デプロイが成功すると、URLが表示されます：
```
https://bakery-system.onrender.com
```

ブラウザでアクセスして動作確認してください。

**注意**: 初回アクセス時は起動に30秒〜1分かかる場合があります（無料プランの制限）。

## 注意事項

### 無料プランの制限

- 15分間アクセスがないとスリープモードになります
- 初回アクセス時に起動まで30秒〜1分かかります
- 月750時間まで無料（1ヶ月分以上）

### データベース

- PostgreSQL無料プランは90日間有効
- 90日後も継続利用可能（無料）
- バックアップは手動で行う必要があります

## トラブルシューティング

### ビルドエラー

**エラー**: `Requirements not found`
- **原因**: requirements.txtが見つからない
- **解決**: Root Directoryが正しく設定されているか確認

**エラー**: `Module not found`
- **原因**: 依存パッケージがインストールされていない
- **解決**: requirements.txtに必要なパッケージが含まれているか確認

### データベース接続エラー

**エラー**: `could not connect to server`
- **原因**: DATABASE_URLが正しく設定されていない
- **解決**: 環境変数のDATABASE_URLを確認

**エラー**: `could not translate host name "dpg-xxx-a" to address`
- **原因**: Internal Database URLが短縮形式でホスト名が不完全
- **解決**: External Database URLを使用（完全なホスト名 `.singapore-postgres.render.com` を含む）
- **例**:
  - NG: `postgresql://user:pass@dpg-xxx-a/db`
  - OK: `postgresql://user:pass@dpg-xxx-a.singapore-postgres.render.com/db`

### アプリケーションが起動しない

**エラー**: `Application failed to start`
- **原因**: Start Commandが間違っている
- **解決**: Start Commandが `gunicorn -w 4 -b 0.0.0.0:$PORT run:app` になっているか確認

**エラー**: `Failed to find attribute 'app' in 'app'`
- **原因**: Gunicornがappオブジェクトを見つけられない、またはポート指定が不足
- **解決**: Start Commandを `gunicorn -w 4 -b 0.0.0.0:$PORT run:app` に変更

## 更新のデプロイ

コードを更新してGitHubにプッシュすると、自動的に再デプロイされます：

```bash
git add .
git commit -m "Update: 説明"
git push origin main
```

Renderが自動的に：
1. 新しいコードを検出
2. ビルドを実行
3. デプロイ

## カスタムドメインの設定（オプション）

有料プランでカスタムドメインを設定できます：

1. Webサービスの `Settings` → `Custom Domain`
2. ドメインを追加
3. DNSレコードを設定

## 環境変数の管理

本番環境で推奨される環境変数：

```
SECRET_KEY=ランダムな長い文字列
DATABASE_URL=PostgreSQLのURL
FLASK_ENV=production
```

## モニタリング

Renderダッシュボードで以下を確認できます：
- デプロイ履歴
- ログ
- メトリクス（CPU、メモリ使用量）
- アクセス数

## バックアップ

定期的にデータをバックアップすることを推奨：

1. データベースのダンプを取得
2. ローカルに保存
3. 必要に応じて復元

## サポート

問題が発生した場合：
1. Renderのログを確認
2. GitHubのIssuesで質問
3. Renderのドキュメントを参照: https://render.com/docs

---

**デプロイ完了後、アプリケーションをお楽しみください！**
