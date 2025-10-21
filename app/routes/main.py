from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Recipe, Ingredient, CostSetting

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def index():
    """ダッシュボード"""
    # 統計情報の取得
    total_recipes = Recipe.query.filter_by(store_id=current_user.id).count()
    total_ingredients = Ingredient.query.filter_by(store_id=current_user.id).count()

    # 最近のレシピ
    recent_recipes = Recipe.query.filter_by(store_id=current_user.id)\
        .order_by(Recipe.updated_at.desc())\
        .limit(5)\
        .all()

    # 原価計算設定
    cost_setting = CostSetting.query.filter_by(store_id=current_user.id).first()

    return render_template('main/index.html',
                         total_recipes=total_recipes,
                         total_ingredients=total_ingredients,
                         recent_recipes=recent_recipes,
                         cost_setting=cost_setting)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """設定画面"""
    from app.forms import CostSettingForm
    from app.models import db

    cost_setting = CostSetting.query.filter_by(store_id=current_user.id).first()

    if not cost_setting:
        cost_setting = CostSetting(store_id=current_user.id)
        db.session.add(cost_setting)
        db.session.commit()

    form = CostSettingForm(obj=cost_setting)

    if form.validate_on_submit():
        form.populate_obj(cost_setting)
        db.session.commit()
        from flask import flash
        flash('設定を保存しました', 'success')
        from flask import redirect, url_for
        return redirect(url_for('main.settings'))

    return render_template('main/settings.html', form=form, cost_setting=cost_setting)
