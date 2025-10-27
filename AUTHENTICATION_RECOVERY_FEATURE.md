# 認証復旧機能の実装ドキュメント

## 概要
パン屋管理システムに、パスワードリセット機能とログインID復旧機能を追加しました。小規模な店舗運営に適した、メール認証不要のシンプルな復旧システムです。

## 実装日
2025年10月27日

## 背景と要件

### ユーザーからの要望
1. **パスワードリセット**: 「ログイン時にパスワード忘れることがある。ログイン画面でパスワード再設定できる必要がある」
2. **ログインID復旧**: 「IDを忘れた場合はどうしますか？」

### 設計方針
- メール認証は不要（小規模店舗向けのシンプルな運用）
- ログインIDがわかればパスワードをリセット可能
- 店舗名でログインIDを検索可能
- セキュリティ警告を表示してログインIDの保護を促す

## 実装内容

### 1. パスワードリセット機能

#### 1.1 フォームの追加 (`app/forms.py`)
```python
class PasswordResetForm(FlaskForm):
    """パスワードリセットフォーム"""
    login_id = StringField('ログインID', validators=[
        DataRequired(message='ログインIDを入力してください')
    ])
    new_password = PasswordField('新しいパスワード', validators=[
        DataRequired(message='新しいパスワードを入力してください'),
        Length(min=6, message='パスワードは6文字以上で設定してください')
    ])
    confirm_password = PasswordField('新しいパスワード（確認）', validators=[
        DataRequired(message='パスワードの確認入力をしてください'),
        EqualTo('new_password', message='パスワードが一致しません')
    ])
    submit = SubmitField('パスワードを変更')
```

**実装のポイント:**
- `login_id`: ログインIDで本人確認
- `new_password`: 6文字以上の新しいパスワード
- `confirm_password`: 入力ミス防止のための確認入力
- `EqualTo`バリデータで2つのパスワードが一致することを確認

#### 1.2 ルート実装 (`app/routes/auth.py`)
```python
@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """パスワードリセット"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        store = Store.query.filter_by(login_id=form.login_id.data).first()
        if store:
            store.set_password(form.new_password.data)
            db.session.commit()
            flash('パスワードを変更しました', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('ログインIDが見つかりません', 'danger')

    return render_template('auth/reset_password.html', form=form)
```

**処理フロー:**
1. ログイン済みユーザーはトップページへリダイレクト
2. フォーム送信時、入力されたログインIDでストアを検索
3. ストアが見つかれば、`set_password()`メソッドで新しいパスワードをハッシュ化して保存
4. 成功メッセージを表示してログインページへ

#### 1.3 テンプレート (`app/templates/auth/reset_password.html`)
主な機能:
- Bootstrap 5を使用したレスポンシブデザイン
- パスワード入力フィールドに表示/非表示トグル機能
- セキュリティ警告の表示
- ログインIDを忘れた場合のリンク

### 2. ログインID復旧機能

#### 2.1 フォームの追加 (`app/forms.py`)
```python
class ForgotLoginIDForm(FlaskForm):
    """ログインID検索フォーム"""
    store_name = StringField('店舗名', validators=[
        DataRequired(message='店舗名を入力してください')
    ])
    submit = SubmitField('検索')
```

**実装のポイント:**
- シンプルな店舗名入力のみ
- 部分一致検索に対応

#### 2.2 ルート実装 (`app/routes/auth.py`)
```python
@bp.route('/forgot-login-id', methods=['GET', 'POST'])
def forgot_login_id():
    """ログインID検索"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgotLoginIDForm()
    found_stores = []

    if form.validate_on_submit():
        # 店舗名で部分一致検索
        found_stores = Store.query.filter(
            Store.store_name.like(f'%{form.store_name.data}%')
        ).all()

        if not found_stores:
            flash('該当する店舗が見つかりませんでした', 'warning')

    return render_template('auth/forgot_login_id.html',
                         form=form,
                         found_stores=found_stores)
```

**処理フロー:**
1. 店舗名で部分一致検索（`LIKE %店舗名%`）
2. 見つかった店舗のリストを表示
3. 各店舗のログインIDを表示
4. ログインまたはパスワードリセットへの直接リンクを提供

#### 2.3 テンプレート (`app/templates/auth/forgot_login_id.html`)
主な機能:
- 店舗名の部分一致検索フォーム
- 検索結果の一覧表示（店舗名とログインID）
- 各店舗に対して「ログイン」「パスワードリセット」ボタンを表示
- 検索結果がない場合の案内メッセージ

### 3. ナビゲーション統合

#### 3.1 ログインページの更新 (`app/templates/auth/login.html`)
```html
<div class="text-center">
    <a href="{{ url_for('auth.forgot_login_id') }}" class="text-decoration-none me-3">
        ログインIDを忘れた
    </a>
    <a href="{{ url_for('auth.reset_password') }}" class="text-decoration-none">
        パスワードを忘れた
    </a>
</div>
```

**実装のポイント:**
- ログインフォームの下に2つのリンクを配置
- ユーザーが適切な復旧方法を選択できるようにする

#### 3.2 相互リンク
- パスワードリセットページ → ログインID検索ページへのリンク
- ログインID検索結果 → ログインページ、パスワードリセットページへのリンク
- すべてのページからログインページに戻れる

## 技術的な詳細

### セキュリティ考慮事項

1. **パスワードのハッシュ化**
   - `werkzeug.security.generate_password_hash()`を使用
   - `set_password()`メソッドで安全にハッシュ化

2. **セキュリティ警告**
   - ログインIDの保護の重要性を警告
   - 店舗名からログインIDが推測できることを明示

3. **認証状態チェック**
   - ログイン済みユーザーは復旧ページにアクセス不可
   - トップページへリダイレクト

### データベースクエリ

1. **ログインIDでの検索**
```python
Store.query.filter_by(login_id=form.login_id.data).first()
```

2. **店舗名での部分一致検索**
```python
Store.query.filter(Store.store_name.like(f'%{form.store_name.data}%')).all()
```

### UI/UX設計

1. **レスポンシブデザイン**
   - Bootstrap 5のグリッドシステムを使用
   - モバイル端末でも使いやすい

2. **パスワード表示トグル**
   - 入力確認のためのパスワード表示/非表示機能
   - JavaScriptで実装

3. **フラッシュメッセージ**
   - 成功: `success`クラス（緑色）
   - 警告: `warning`クラス（黄色）
   - エラー: `danger`クラス（赤色）

## 使用フロー

### ケース1: パスワードを忘れた場合（ログインIDは覚えている）
1. ログインページで「パスワードを忘れた」をクリック
2. ログインIDを入力
3. 新しいパスワードを入力（2回）
4. パスワード変更完了
5. ログインページへ遷移

### ケース2: ログインIDを忘れた場合
1. ログインページで「ログインIDを忘れた」をクリック
2. 店舗名を入力（部分一致可）
3. 検索結果から自分の店舗のログインIDを確認
4. オプション:
   - 「ログイン」ボタンでログインページへ（ログインIDが自動入力）
   - 「パスワードリセット」ボタンでパスワードリセットページへ（ログインIDが自動入力）

### ケース3: 両方忘れた場合
1. 「ログインIDを忘れた」から開始
2. 店舗名で検索してログインIDを取得
3. 「パスワードリセット」ボタンをクリック
4. 新しいパスワードを設定
5. ログイン

## テスト結果

### 実施したテスト
1. **パスワードリセット機能**
   - ✓ 正しいログインIDでパスワード変更成功
   - ✓ 存在しないログインIDでエラーメッセージ表示
   - ✓ パスワード不一致でバリデーションエラー
   - ✓ 6文字未満のパスワードでバリデーションエラー

2. **ログインID検索機能**
   - ✓ 店舗名「satoe」で検索してログインID「takahashi」を発見
   - ✓ 部分一致検索が正常に動作
   - ✓ 検索結果が見つからない場合の警告表示

3. **統合テスト**
   - ✓ ログインページから各復旧ページへのナビゲーション
   - ✓ 復旧完了後のログインフロー
   - ✓ サーバーログで正常な動作を確認（2025-10-27 13:15:50）

## ファイル一覧

### 新規作成ファイル
1. `app/templates/auth/reset_password.html` - パスワードリセットページ
2. `app/templates/auth/forgot_login_id.html` - ログインID検索ページ
3. `AUTHENTICATION_RECOVERY_FEATURE.md` - 本ドキュメント

### 変更ファイル
1. `app/forms.py` - フォームクラス追加
2. `app/routes/auth.py` - ルート追加
3. `app/templates/auth/login.html` - ナビゲーションリンク追加

## 今後の改善案

### セキュリティ強化
1. **二段階認証**: SMS認証やメール認証の追加
2. **パスワード強度チェック**: 数字、大文字、記号の組み合わせ要求
3. **リセット回数制限**: 短時間での連続リセット防止
4. **セッションタイムアウト**: 一定時間後の自動ログアウト

### 機能拡張
1. **パスワード変更履歴**: 過去のパスワード再利用防止
2. **セキュリティ質問**: ログインID検索時の追加認証
3. **管理者通知**: パスワードリセット時の管理者への通知
4. **ログイン履歴**: 不審なアクセスの検出

### UI/UX改善
1. **パスワード強度インジケーター**: リアルタイムでパスワードの強度を表示
2. **キーボードショートカット**: フォーム操作の効率化
3. **多言語対応**: 英語、その他言語のサポート

## 関連ドキュメント
- [原価計算修正と販売価格機能](COST_CALCULATION_FIX_AND_SELLING_PRICE_FEATURE.md)
- [ラベルサイズカスタマイズ機能](LABEL_SIZE_CUSTOMIZATION_FEATURE.md)

## まとめ
パスワードリセットとログインID復旧機能を実装し、ユーザーが自力でアカウントアクセスを回復できるようになりました。小規模な店舗運営に適した、シンプルで使いやすい認証復旧システムです。

---
作成日: 2025年10月27日
最終更新: 2025年10月27日
