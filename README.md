# パン屋向け原価計算アプリケーション

複数のパン屋が利用できる原価計算・商品ラベル作成アプリケーションです。

## 主な機能

### 1. ユーザー認証・管理
- 店舗ごとのアカウント登録・ログイン
- パスワード変更機能
- セキュアな認証（bcryptによるパスワードハッシュ化）

### 2. 材料マスタ管理
- 材料の登録・編集・削除
- 単価、単位、仕入先の管理
- アレルゲン情報の設定

### 3. レシピ管理
- レシピの登録・編集・削除
- 材料リストの管理
- 製造個数・製造時間の設定
- カテゴリー分類（食パン、菓子パン、調理パンなど）

### 4. 原価計算
- 材料費の自動計算
- 人件費の計算（時給 × 製造時間）
- 光熱費の計算（月額を時間按分）
- 1個あたりの原価計算
- 販売推奨価格の算出（利益率設定）

### 5. 商品ラベル作成
- PDF形式での商品ラベル出力
- A4用紙に8枚（2列×4行）印刷
- ラベル内容：
  - 商品名
  - 材料一覧
  - アレルゲン表示
  - 製造日・賞味期限
  - 原価・販売価格（オプション）
  - 店舗名

## 技術スタック

- **バックエンド**: Python 3.x + Flask
- **データベース**: SQLite（開発）/ PostgreSQL（本番想定）
- **認証**: Flask-Login
- **フォーム**: Flask-WTF + WTForms
- **PDF生成**: ReportLab
- **フロントエンド**: Bootstrap 5 + Bootstrap Icons

## セットアップ手順

### 1. 前提条件

- Python 3.8以上
- pip（Pythonパッケージマネージャー）

### 2. インストール

```bash
# リポジトリのクローン（または解凍）
cd bakery_cost_calculator

# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
# .env.exampleをコピーして.envを作成
copy .env.example .env  # Windows
# または
cp .env.example .env    # macOS/Linux

# .envファイルを編集してSECRET_KEYを設定
# 本番環境では必ず強力なランダム文字列に変更してください
```

### 4. データベースの初期化

アプリケーションを初回起動すると、自動的にデータベースが作成されます。

### 5. アプリケーションの起動

```bash
python run.py
```

アプリケーションは `http://localhost:5000` で起動します。

## 使い方

### 初回セットアップ

1. **店舗登録**
   - `http://localhost:5000/auth/register` にアクセス
   - ログインID、店舗名、パスワードを入力して登録

2. **ログイン**
   - 登録したログインIDとパスワードでログイン

3. **原価計算設定**
   - 「設定」メニューから原価計算方法を設定
   - 人件費・光熱費の計算が必要な場合は該当項目にチェック
   - 時給、月額光熱費、利益率を設定

4. **材料登録**
   - 「材料管理」から使用する材料を登録
   - 材料名、単価、単位、アレルゲン情報を入力

5. **レシピ作成**
   - 「レシピ管理」から新規レシピを作成
   - 商品情報を入力後、使用する材料と使用量を設定

6. **原価確認**
   - レシピ詳細ページで自動計算された原価を確認

7. **ラベル印刷**
   - レシピ詳細ページから「ラベル作成」をクリック
   - 製造日や表示オプションを設定してPDFをダウンロード

## プロジェクト構造

```
bakery_cost_calculator/
├── app/
│   ├── __init__.py          # アプリケーションファクトリ
│   ├── models.py            # データベースモデル
│   ├── forms.py             # WTFormsフォーム定義
│   ├── routes/              # ルート定義
│   │   ├── auth.py          # 認証関連
│   │   ├── main.py          # メインページ
│   │   ├── ingredients.py   # 材料管理
│   │   ├── recipes.py       # レシピ管理
│   │   └── labels.py        # ラベル生成
│   ├── templates/           # HTMLテンプレート
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── main/
│   │   ├── ingredients/
│   │   ├── recipes/
│   │   └── labels/
│   └── static/              # 静的ファイル
│       └── css/
│           └── style.css
├── instance/                # インスタンス固有ファイル（DB等）
├── run.py                   # アプリケーション起動スクリプト
├── requirements.txt         # 依存パッケージリスト
├── .env.example            # 環境変数サンプル
└── README.md               # このファイル
```

## データベース設計

### 主要テーブル

- **stores**: 店舗情報
- **cost_settings**: 原価計算設定
- **ingredients**: 材料マスタ
- **recipes**: レシピ
- **recipe_ingredients**: レシピと材料の関連

詳細は `app/models.py` を参照してください。

## セキュリティ

- パスワードはbcryptでハッシュ化
- CSRF対策（Flask-WTF）
- セッション管理（Flask-Login）
- 店舗間のデータアクセス制御

## カスタマイズ

### 原価計算方法の変更

`app/models.py` の `Recipe.calculate_total_cost()` メソッドを編集してください。

### ラベルデザインの変更

`app/routes/labels.py` の `draw_label()` 関数を編集してください。

### カテゴリーの追加

`app/forms.py` の `RecipeForm` クラスの `category` フィールドの選択肢を編集してください。

## 本番環境へのデプロイ

### 環境変数の設定

```bash
# 本番用の強力なシークレットキーを生成
python -c "import secrets; print(secrets.token_hex(32))"

# .envファイルに設定
SECRET_KEY=生成されたキー
FLASK_ENV=production
FLASK_DEBUG=False
```

### PostgreSQLへの移行

```bash
# PostgreSQLをインストール後、データベースを作成
createdb bakery_db

# .envファイルのDATABASE_URLを変更
DATABASE_URL=postgresql://username:password@localhost/bakery_db
```

### Gunicornでの起動（本番推奨）

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## トラブルシューティング

### データベースエラー

```bash
# データベースファイルを削除して再作成
rm instance/bakery.db
python run.py
```

### PDF生成エラー（日本語フォント）

Windowsの場合、`app/routes/labels.py` の `register_fonts()` 関数でフォントパスを確認してください。

### ポート競合

```bash
# 別のポートで起動
# run.pyの最終行を編集
app.run(debug=True, host='0.0.0.0', port=8000)
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## サポート

問題が発生した場合は、以下を確認してください：
- Python及び依存パッケージのバージョン
- エラーメッセージの内容
- 環境変数の設定

## 今後の機能拡張案

- [ ] レポート機能（原価率分析、利益シミュレーション）
- [ ] CSV/Excelエクスポート
- [ ] 材料の在庫管理
- [ ] レシピのバージョン管理
- [ ] ユーザー権限管理（管理者/スタッフ）
- [ ] APIエンドポイントの提供
- [ ] モバイル対応の改善
- [ ] ダークモード対応

## 開発者向け

### テストの実行

```bash
# テストディレクトリを作成して実行
pytest tests/
```

### 開発モードでの起動

```bash
# 環境変数を設定
export FLASK_ENV=development
export FLASK_DEBUG=True

# 起動
python run.py
```

## バージョン履歴

- **v1.0.0** (2025-01-21)
  - 初回リリース
  - 基本機能の実装（認証、材料管理、レシピ管理、原価計算、ラベル生成）
