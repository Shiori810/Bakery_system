from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Store, CostSetting
from app.forms import RegistrationForm, LoginForm, PasswordChangeForm, PasswordResetForm, ForgotLoginIDForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """店舗登録"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # 新しい店舗を作成
        store = Store(
            login_id=form.login_id.data,
            store_name=form.store_name.data
        )
        store.set_password(form.password.data)

        db.session.add(store)
        db.session.commit()

        # デフォルトの原価計算設定を作成
        cost_setting = CostSetting(store_id=store.id)
        db.session.add(cost_setting)
        db.session.commit()

        flash('店舗登録が完了しました。ログインしてください。', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        store = Store.query.filter_by(login_id=form.login_id.data).first()

        if store and store.check_password(form.password.data):
            login_user(store)
            flash(f'ようこそ、{store.store_name}さん', 'success')

            # next パラメータがあればそこへリダイレクト
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('ログインIDまたはパスワードが正しくありません', 'danger')

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """ログアウト"""
    logout_user()
    flash('ログアウトしました', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """パスワード変更"""
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('パスワードを変更しました', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('現在のパスワードが正しくありません', 'danger')

    return render_template('auth/change_password.html', form=form)


@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """パスワードリセット"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        store = Store.query.filter_by(login_id=form.login_id.data).first()

        if store:
            # パスワードをリセット
            store.set_password(form.new_password.data)
            db.session.commit()
            flash('パスワードをリセットしました。新しいパスワードでログインしてください。', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('入力されたログインIDは存在しません', 'danger')

    return render_template('auth/reset_password.html', form=form)


@bp.route('/forgot-login-id', methods=['GET', 'POST'])
def forgot_login_id():
    """ログインID確認"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgotLoginIDForm()
    found_stores = None

    if form.validate_on_submit():
        # 店舗名で検索（部分一致）
        found_stores = Store.query.filter(Store.store_name.like(f'%{form.store_name.data}%')).all()

        if not found_stores:
            flash('該当する店舗が見つかりませんでした', 'warning')

    return render_template('auth/forgot_login_id.html', form=form, found_stores=found_stores)
