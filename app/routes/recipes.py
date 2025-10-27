from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Recipe, Ingredient, RecipeIngredient, CostSetting
from app.forms import RecipeForm

bp = Blueprint('recipes', __name__, url_prefix='/recipes')


@bp.route('/')
@login_required
def index():
    """レシピ一覧"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category = request.args.get('category', '', type=str)

    query = Recipe.query.filter_by(store_id=current_user.id)

    if search:
        query = query.filter(Recipe.product_name.like(f'%{search}%'))

    if category:
        query = query.filter_by(category=category)

    recipes = query.order_by(Recipe.updated_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)

    # 原価計算設定の取得
    cost_setting = CostSetting.query.filter_by(store_id=current_user.id).first()

    return render_template('recipes/index.html',
                         recipes=recipes,
                         cost_setting=cost_setting,
                         search=search,
                         category=category)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """レシピ登録"""
    form = RecipeForm()

    if form.validate_on_submit():
        recipe = Recipe(
            store_id=current_user.id,
            product_name=form.product_name.data,
            category=form.category.data,
            production_quantity=form.production_quantity.data,
            production_time=form.production_time.data,
            shelf_life_days=form.shelf_life_days.data,
            custom_profit_margin=form.custom_profit_margin.data,
            selling_price=form.selling_price.data
        )

        db.session.add(recipe)
        db.session.commit()

        flash(f'レシピ「{recipe.product_name}」を登録しました', 'success')
        return redirect(url_for('recipes.edit_ingredients', id=recipe.id))

    return render_template('recipes/form.html', form=form, title='レシピ登録')


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """レシピ編集"""
    recipe = Recipe.query.filter_by(id=id, store_id=current_user.id).first_or_404()

    form = RecipeForm(obj=recipe)

    if form.validate_on_submit():
        form.populate_obj(recipe)
        db.session.commit()

        flash(f'レシピ「{recipe.product_name}」を更新しました', 'success')
        return redirect(url_for('recipes.detail', id=recipe.id))

    return render_template('recipes/form.html',
                         form=form,
                         recipe=recipe,
                         title='レシピ編集')


@bp.route('/<int:id>/detail')
@login_required
def detail(id):
    """レシピ詳細"""
    from app.models import CustomCostItem

    recipe = Recipe.query.filter_by(id=id, store_id=current_user.id).first_or_404()
    cost_setting = CostSetting.query.filter_by(store_id=current_user.id).first()

    # 原価計算
    material_cost = recipe.calculate_material_cost()
    total_cost = recipe.calculate_total_cost(cost_setting)
    unit_cost = recipe.calculate_unit_cost(cost_setting)
    suggested_price = recipe.get_selling_price(cost_setting) if cost_setting else unit_cost

    # カスタム原価項目の取得
    custom_cost_items = CustomCostItem.query.filter_by(
        store_id=current_user.id,
        is_active=True
    ).order_by(CustomCostItem.display_order).all()

    return render_template('recipes/detail.html',
                         recipe=recipe,
                         cost_setting=cost_setting,
                         material_cost=material_cost,
                         total_cost=total_cost,
                         unit_cost=unit_cost,
                         suggested_price=suggested_price,
                         custom_cost_items=custom_cost_items)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """レシピ削除"""
    recipe = Recipe.query.filter_by(id=id, store_id=current_user.id).first_or_404()

    name = recipe.product_name
    db.session.delete(recipe)
    db.session.commit()

    flash(f'レシピ「{name}」を削除しました', 'info')
    return redirect(url_for('recipes.index'))


@bp.route('/<int:id>/ingredients/edit', methods=['GET', 'POST'])
@login_required
def edit_ingredients(id):
    """レシピ材料編集"""
    recipe = Recipe.query.filter_by(id=id, store_id=current_user.id).first_or_404()
    ingredients = Ingredient.query.filter_by(store_id=current_user.id)\
        .order_by(Ingredient.name).all()

    if request.method == 'POST':
        # 既存の材料関連を削除
        RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

        # 新しい材料を追加
        ingredient_ids = request.form.getlist('ingredient_id[]')
        quantities = request.form.getlist('quantity[]')

        for ingredient_id, quantity in zip(ingredient_ids, quantities):
            if ingredient_id and quantity:
                try:
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=int(ingredient_id),
                        quantity=float(quantity)
                    )
                    db.session.add(recipe_ingredient)
                except (ValueError, TypeError):
                    continue

        db.session.commit()
        flash('材料を更新しました', 'success')
        return redirect(url_for('recipes.detail', id=recipe.id))

    return render_template('recipes/edit_ingredients.html',
                         recipe=recipe,
                         ingredients=ingredients)


@bp.route('/<int:id>/ingredients/api', methods=['GET'])
@login_required
def get_ingredients_api(id):
    """レシピ材料取得API(JSON)"""
    recipe = Recipe.query.filter_by(id=id, store_id=current_user.id).first_or_404()

    ingredients_data = []
    for ri in recipe.recipe_ingredients:
        ingredients_data.append({
            'id': ri.ingredient.id,
            'name': ri.ingredient.name,
            'quantity': float(ri.quantity),
            'unit': ri.ingredient.unit,
            'unit_price': float(ri.ingredient.unit_price)
        })

    return jsonify(ingredients_data)
