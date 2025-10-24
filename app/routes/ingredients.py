from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Ingredient
from app.forms import IngredientForm

bp = Blueprint('ingredients', __name__, url_prefix='/ingredients')


@bp.route('/')
@login_required
def index():
    """材料一覧"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = Ingredient.query.filter_by(store_id=current_user.id)

    if search:
        query = query.filter(Ingredient.name.like(f'%{search}%'))

    ingredients = query.order_by(Ingredient.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)

    return render_template('ingredients/index.html',
                         ingredients=ingredients,
                         search=search)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """材料登録"""
    form = IngredientForm()

    if form.validate_on_submit():
        ingredient = Ingredient(
            store_id=current_user.id,
            name=form.name.data,
            purchase_price=form.purchase_price.data if form.purchase_price.data else None,
            purchase_quantity=form.purchase_quantity.data if form.purchase_quantity.data else 1,
            purchase_unit=form.purchase_unit.data if form.purchase_unit.data else None,
            usage_unit=form.usage_unit.data if form.usage_unit.data else None,
            supplier=form.supplier.data,
            is_allergen=form.is_allergen.data,
            allergen_type=form.allergen_type.data if form.is_allergen.data else None
        )

        db.session.add(ingredient)
        db.session.commit()

        flash(f'材料「{ingredient.name}」を登録しました', 'success')
        return redirect(url_for('ingredients.index'))

    return render_template('ingredients/form.html', form=form, title='材料登録')


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """材料編集"""
    ingredient = Ingredient.query.filter_by(id=id, store_id=current_user.id).first_or_404()

    form = IngredientForm(obj=ingredient)

    if form.validate_on_submit():
        form.populate_obj(ingredient)
        if not ingredient.is_allergen:
            ingredient.allergen_type = None

        db.session.commit()

        flash(f'材料「{ingredient.name}」を更新しました', 'success')
        return redirect(url_for('ingredients.index'))

    return render_template('ingredients/form.html',
                         form=form,
                         ingredient=ingredient,
                         title='材料編集')


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """材料削除"""
    ingredient = Ingredient.query.filter_by(id=id, store_id=current_user.id).first_or_404()

    # レシピで使用されているかチェック
    if ingredient.recipe_ingredients:
        flash(f'材料「{ingredient.name}」はレシピで使用されているため削除できません', 'danger')
        return redirect(url_for('ingredients.index'))

    name = ingredient.name
    db.session.delete(ingredient)
    db.session.commit()

    flash(f'材料「{name}」を削除しました', 'info')
    return redirect(url_for('ingredients.index'))
