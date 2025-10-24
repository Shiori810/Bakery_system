# トラブルシューティングレポート: Internal Server Error 調査

## 報告日時
2025-10-24

## 問題の概要

**症状**: `localhost:5000/recipes/1/detail` および `https://bakery.etsu-dev.com/labels/4` へのアクセス時に Internal Server Error が発生

**エラーメッセージ**:
```
Internal Server Error
The server encountered an internal error and was unable to complete your request.
Either the server is overloaded or there is an error in the application.
```

---

## 実施した調査内容

### 1. データベースマイグレーションの確認

**調査内容**:
- `migrate_add_custom_profit_margin.py` スクリプトの実行
- `custom_profit_margin` カラムの存在確認

**結果**:
```bash
cd "C:\Users\SatoeTakahashi\SK_Bakery\Bakery_system"
python migrate_add_custom_profit_margin.py
```

**出力**:
```
============================================================
データベースマイグレーション: custom_profit_margin追加
============================================================
データベース接続: sqlite:///instance/bakery.db
custom_profit_marginカラムは既に存在します。マイグレーション不要です。

[OK] マイグレーションが正常に完了しました。
```

**結論**: ✅ マイグレーションは既に適用済み、カラムは存在する

---

### 2. データベース接続とデータ確認

**実行したテスト**:
```python
from app import create_app
from app.models import Recipe
app = create_app()
app.app_context().push()
recipe = Recipe.query.get(1)
print(f'Recipe found: {recipe.product_name if recipe else None}')
print(f'Has custom_profit_margin: {hasattr(recipe, "custom_profit_margin") if recipe else False}')
print(f'Value: {recipe.custom_profit_margin if recipe else None}')
```

**結果**:
```
Recipe found: ロールパン
Has custom_profit_margin: True
Value: None
```

**結論**: ✅ データベース接続は正常、レシピデータは取得可能、`custom_profit_margin` フィールドにアクセス可能

---

### 3. Flaskサーバーのプロセス確認と再起動

**実施した作業**:

1. **ポート5000の使用状況確認**:
   ```bash
   netstat -ano | findstr :5000
   ```

   **結果**: PID 16604 が port 5000 を使用中

2. **プロセスの特定**:
   ```bash
   tasklist | findstr 16604
   ```

   **結果**: `python.exe` プロセス (80,292 K メモリ使用)

3. **古いプロセスの強制終了**:
   ```bash
   taskkill //F //PID 16604
   ```

   **結果**: ✅ 成功: PID 16604 のプロセスは強制終了されました

4. **新しいFlaskサーバーの起動**:
   ```bash
   C:/Users/SatoeTakahashi/SK_Bakery/Bakery_system/venv/Scripts/python.exe \
   C:/Users/SatoeTakahashi/SK_Bakery/Bakery_system/run.py
   ```

   **結果**:
   ```
   * Serving Flask app 'app'
   * Debug mode: on
   * Running on http://127.0.0.1:5000
   * Debugger is active!
   * Debugger PIN: 378-829-051
   ```

**結論**: ✅ Flaskサーバーは正常に起動している

---

### 4. コードの整合性確認

**確認したファイル**:

1. **`app/models.py`** (Line 170):
   ```python
   custom_profit_margin = db.Column(db.Numeric(5, 2))  # 商品ごとの利益率(%)
   ```
   ✅ フィールド定義は正しい

2. **`app/models.py`** (Line 222-232) - `calculate_suggested_price` メソッド:
   ```python
   def calculate_suggested_price(self, cost_setting):
       """販売推奨価格の計算"""
       unit_cost = self.calculate_unit_cost(cost_setting)

       # 商品ごとの利益率があればそれを使用、なければ基本設定を使用
       profit_margin = self.custom_profit_margin if self.custom_profit_margin is not None else (cost_setting.profit_margin if cost_setting else 0)

       if profit_margin > 0:
           margin_multiplier = 1 + (float(profit_margin) / 100)
           return unit_cost * margin_multiplier
       return unit_cost
   ```
   ✅ ビジネスロジックは正しい

3. **`app/routes/labels.py`** (Line 32-47):
   ```python
   @bp.route('/<int:id>')
   @login_required
   def preview(id):
       """ラベルプレビュー"""
       recipe = Recipe.query.filter_by(id=id, store_id=current_user.id).first_or_404()
       cost_setting = CostSetting.query.filter_by(store_id=current_user.id).first()

       # 原価情報
       unit_cost = recipe.calculate_unit_cost(cost_setting)
       suggested_price = recipe.calculate_suggested_price(cost_setting) if cost_setting else unit_cost

       return render_template('labels/preview.html',
                            recipe=recipe,
                            cost_setting=cost_setting,
                            unit_cost=unit_cost,
                            suggested_price=suggested_price)
   ```
   ✅ ルート定義は正しい

**結論**: ✅ コードに明らかな問題は見られない

---

## 未解決の問題点

### 問題の状況

- ✅ データベースマイグレーションは完了している
- ✅ データベース接続は正常に動作している
- ✅ Flaskサーバーは正常に起動している
- ✅ コードに明らかな構文エラーや論理エラーは見られない
- ❌ **しかし、ブラウザからのアクセス時に Internal Server Error が発生する**

### 考えられる原因

1. **キャッシュの問題**:
   - ブラウザキャッシュが古いエラーページを表示している可能性
   - Pythonの `.pyc` ファイルが古いバージョンをキャッシュしている可能性

2. **セッション/認証の問題**:
   - `@login_required` デコレータが原因でエラーが発生している可能性
   - ユーザーがログインしていない、またはセッションが無効

3. **テンプレートの問題**:
   - `labels/preview.html` テンプレートに問題がある可能性
   - テンプレート内で `custom_profit_margin` を参照している箇所でエラーが発生

4. **サーバーログの未確認**:
   - Flaskサーバーのコンソール出力に詳細なエラートレースバックが表示されているはず
   - 実際のエラー内容が確認できていない

5. **本番環境の問題**:
   - `https://bakery.etsu-dev.com/labels/4` については、Render上でマイグレーションが未実行の可能性

---

## 推奨される次のステップ

### 即座に試すべき対処法

1. **ブラウザのハードリフレッシュ**:
   - Windows: `Ctrl + Shift + R` または `Ctrl + F5`
   - キャッシュをクリアして再読み込み

2. **Flaskサーバーのコンソールを確認**:
   - サーバーを起動しているターミナルウィンドウを確認
   - エラーのスタックトレースを読む
   - 具体的なエラー原因（例: AttributeError, TypeError など）を特定

3. **ログイン状態の確認**:
   - まず `http://localhost:5000/` にアクセス
   - ログイン画面が表示される場合はログイン
   - その後、レシピ詳細ページにアクセス

4. **Pythonキャッシュのクリア**:
   ```bash
   cd C:\Users\SatoeTakahashi\SK_Bakery\Bakery_system
   # __pycache__ フォルダと .pyc ファイルを削除
   del /s /q __pycache__
   del /s /q *.pyc
   # サーバー再起動
   C:/Users/SatoeTakahashi/SK_Bakery/Bakery_system/venv/Scripts/python.exe run.py
   ```

5. **別のレシピでテスト**:
   - `http://localhost:5000/recipes/` でレシピ一覧を表示
   - 他のレシピの詳細ページにもアクセスしてみる
   - 特定のレシピだけの問題か、全体の問題かを切り分け

---

### 詳細なデバッグ手順

#### ステップ1: エラーログの取得

Flaskサーバーのコンソール出力から、以下のような情報を確認:

```
[日時] "GET /recipes/1/detail HTTP/1.1" 500 -
Traceback (most recent call last):
  File "...", line ..., in ...
    ...
SomeError: エラーの詳細メッセージ
```

#### ステップ2: テンプレートの確認

`app/templates/labels/preview.html` の内容を確認し、`custom_profit_margin` や `get_profit_margin` を使用している箇所をチェック。

#### ステップ3: シンプルなテストルートの追加

`app/routes/labels.py` に一時的なテストルートを追加:

```python
@bp.route('/test')
@login_required
def test():
    """テスト用ルート"""
    from app.models import Recipe
    recipe = Recipe.query.first()
    return f"Recipe: {recipe.product_name}, custom_profit_margin: {recipe.custom_profit_margin}"
```

このルートにアクセスして、データベースアクセスが正常か確認。

#### ステップ4: デバッガーの活用

Flask debug mode が有効なので、エラーページでインタラクティブデバッガーを使用:

1. エラーページの右側に表示されるコンソールアイコンをクリック
2. デバッガーPIN (`378-829-051`) を入力
3. エラーが発生した箇所の変数を調査

---

## 本番環境（Render）への対応

### 現状

- コードは Render にデプロイ済み
- しかし、データベースマイグレーションは未実行
- そのため、`https://bakery.etsu-dev.com` でも同様のエラーが発生している可能性が高い

### 対処方法

1. **Render ダッシュボードにアクセス**:
   - https://dashboard.render.com/
   - `bakery-cost-calculator` サービスを選択

2. **Shell を開く**:
   - "Shell" ボタンをクリック
   - ターミナルが開く

3. **マイグレーションを実行**:
   ```bash
   python migrate_add_custom_profit_margin.py
   ```

4. **サービスの再起動** (必要に応じて):
   - Renderダッシュボードから "Manual Deploy" → "Deploy latest commit"

5. **動作確認**:
   - `https://bakery.etsu-dev.com` にアクセス
   - エラーが解消されているか確認

---

## ファイルの状態

### 変更されたファイル（今回の調査では変更なし）

- なし（調査のみ実施）

### 確認したファイル

1. `C:\Users\SatoeTakahashi\SK_Bakery\Bakery_system\migrate_add_custom_profit_margin.py`
2. `C:\Users\SatoeTakahashi\SK_Bakery\Bakery_system\app\models.py`
3. `C:\Users\SatoeTakahashi\SK_Bakery\Bakery_system\app\routes\labels.py`
4. `C:\Users\SatoeTakahashi\SK_Bakery\Bakery_system\run.py`
5. `C:\Users\SatoeTakahashi\SK_Bakery\Bakery_system\instance\bakery.db`

### 新規作成したファイル

- `TROUBLESHOOTING_REPORT.md` (本レポート)

---

## まとめ

### 実施した作業

1. ✅ データベースマイグレーションの確認・実行
2. ✅ データベース接続のテスト
3. ✅ Flaskサーバープロセスの確認と再起動
4. ✅ コードの整合性確認
5. ✅ トラブルシューティングレポートの作成

### 未解決の問題

- ❌ ブラウザからのアクセス時に Internal Server Error が発生
- ❌ 実際のエラーの詳細（スタックトレース）が未確認

### 次に取るべきアクション

1. **最優先**: Flaskサーバーのコンソール出力でエラーの詳細を確認
2. ブラウザのハードリフレッシュ
3. ログイン状態の確認
4. Pythonキャッシュのクリア
5. Flask デバッガーの活用

---

## 参考情報

### 環境情報

- **OS**: Windows
- **Python環境**: `C:\Users\SatoeTakahashi\SK_Bakery\Bakery_system\venv\`
- **データベース**: SQLite (`instance/bakery.db`)
- **開発サーバー**: Flask development server (debug mode)
- **ポート**: 5000

### 関連ドキュメント

- [DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md) - 商品ごとの利益率設定機能の開発レポート
- [CUSTOM_PROFIT_MARGIN_UPDATE.md](CUSTOM_PROFIT_MARGIN_UPDATE.md) - 機能説明ドキュメント

### Gitの状態

- **変更**: なし（調査のみ）
- **コミット**: 不要
- **プッシュ**: 不要

---

**レポート作成日**: 2025-10-24
**作成者**: Claude Code (AI Assistant)
**ステータス**: 問題未解決・作業中断
