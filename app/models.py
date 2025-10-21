from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Store(UserMixin, db.Model):
    """店舗テーブル"""
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # リレーション
    cost_setting = db.relationship('CostSetting', backref='store', uselist=False, cascade='all, delete-orphan')
    ingredients = db.relationship('Ingredient', backref='store', lazy=True, cascade='all, delete-orphan')
    recipes = db.relationship('Recipe', backref='store', lazy=True, cascade='all, delete-orphan')
    custom_cost_items = db.relationship('CustomCostItem', backref='store', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """パスワードをハッシュ化して保存"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """パスワードの検証"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Store {self.store_name}>'


class CostSetting(db.Model):
    """原価計算設定テーブル"""
    __tablename__ = 'cost_settings'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False, unique=True)
    include_labor_cost = db.Column(db.Boolean, default=False)
    include_utility_cost = db.Column(db.Boolean, default=False)
    hourly_wage = db.Column(db.Numeric(10, 2), default=0.0)  # 時給
    monthly_utility_cost = db.Column(db.Numeric(10, 2), default=0.0)  # 月額光熱費
    profit_margin = db.Column(db.Numeric(5, 2), default=30.0)  # 利益率(%)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CostSetting store_id={self.store_id}>'


class Ingredient(db.Model):
    """材料マスタテーブル"""
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)  # 単価
    unit = db.Column(db.String(20), nullable=False)  # 単位(g, kg, ml, L, 個など)
    supplier = db.Column(db.String(100))  # 仕入先(オプション)
    is_allergen = db.Column(db.Boolean, default=False)  # アレルゲンフラグ
    allergen_type = db.Column(db.String(50))  # アレルゲン種類(小麦、卵、乳など)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    recipe_ingredients = db.relationship('RecipeIngredient', backref='ingredient', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Ingredient {self.name}>'


class Recipe(db.Model):
    """レシピテーブル"""
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # 商品カテゴリー
    production_quantity = db.Column(db.Integer, nullable=False, default=1)  # 製造個数
    production_time = db.Column(db.Integer, default=0)  # 製造時間(分)
    shelf_life_days = db.Column(db.Integer)  # 賞味期限(日数)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    recipe_ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy=True, cascade='all, delete-orphan')

    def calculate_material_cost(self):
        """材料費の計算"""
        total_cost = 0
        for ri in self.recipe_ingredients:
            # 単位変換を考慮した計算
            quantity = self._convert_to_base_unit(ri.quantity, ri.ingredient.unit)
            unit_price = self._convert_to_base_unit(ri.ingredient.unit_price, ri.ingredient.unit)
            total_cost += quantity * unit_price
        return float(total_cost)

    def calculate_total_cost(self, cost_setting=None):
        """総原価の計算(固定費含む)"""
        material_cost = self.calculate_material_cost()

        if not cost_setting:
            return material_cost

        total_cost = material_cost

        # 人件費の追加
        if cost_setting.include_labor_cost and self.production_time > 0:
            labor_cost = float(cost_setting.hourly_wage) * (self.production_time / 60)
            total_cost += labor_cost

        # 光熱費の追加(簡易計算: 月額を30日で割って時間按分)
        if cost_setting.include_utility_cost and self.production_time > 0:
            daily_utility = float(cost_setting.monthly_utility_cost) / 30
            hourly_utility = daily_utility / 24
            utility_cost = hourly_utility * (self.production_time / 60)
            total_cost += utility_cost

        # カスタム原価項目の追加
        custom_items = CustomCostItem.query.filter_by(
            store_id=self.store_id,
            is_active=True
        ).all()

        for item in custom_items:
            total_cost += item.calculate_cost(self)

        return total_cost

    def calculate_unit_cost(self, cost_setting=None):
        """1個あたりの原価"""
        total_cost = self.calculate_total_cost(cost_setting)
        return total_cost / self.production_quantity if self.production_quantity > 0 else 0

    def calculate_suggested_price(self, cost_setting):
        """販売推奨価格の計算"""
        unit_cost = self.calculate_unit_cost(cost_setting)
        if cost_setting and cost_setting.profit_margin > 0:
            margin_multiplier = 1 + (float(cost_setting.profit_margin) / 100)
            return unit_cost * margin_multiplier
        return unit_cost

    def get_allergens(self):
        """アレルゲン情報の取得"""
        allergens = []
        for ri in self.recipe_ingredients:
            if ri.ingredient.is_allergen and ri.ingredient.allergen_type:
                if ri.ingredient.allergen_type not in allergens:
                    allergens.append(ri.ingredient.allergen_type)
        return allergens

    @staticmethod
    def _convert_to_base_unit(value, unit):
        """単位を基本単位に変換(簡易版)"""
        # kg -> g, L -> ml の変換
        conversion_factors = {
            'kg': 1000,
            'l': 1000,
            'L': 1000,
        }

        if unit in conversion_factors:
            return float(value) / conversion_factors[unit]
        return float(value)

    def __repr__(self):
        return f'<Recipe {self.product_name}>'


class RecipeIngredient(db.Model):
    """レシピ材料中間テーブル"""
    __tablename__ = 'recipe_ingredients'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    quantity = db.Column(db.Numeric(10, 3), nullable=False)  # 使用量

    def __repr__(self):
        return f'<RecipeIngredient recipe_id={self.recipe_id} ingredient_id={self.ingredient_id}>'


class CustomCostItem(db.Model):
    """カスタム原価項目テーブル"""
    __tablename__ = 'custom_cost_items'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 項目名（例: 包装費、減価償却費など）
    calculation_type = db.Column(db.String(20), nullable=False)  # 計算方法: 'fixed', 'per_unit', 'per_time'
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)  # 金額
    is_active = db.Column(db.Boolean, default=True)  # 有効/無効
    description = db.Column(db.String(255))  # 説明
    display_order = db.Column(db.Integer, default=0)  # 表示順序
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_cost(self, recipe):
        """
        原価を計算

        Args:
            recipe: Recipeオブジェクト

        Returns:
            float: 計算された原価
        """
        if not self.is_active:
            return 0.0

        if self.calculation_type == 'fixed':
            # 固定費: レシピ全体に対して固定金額
            return float(self.amount)

        elif self.calculation_type == 'per_unit':
            # 個数あたり: 製造個数 × 単価
            return float(self.amount) * recipe.production_quantity

        elif self.calculation_type == 'per_time':
            # 時間あたり: 製造時間(分) × 分単価
            if recipe.production_time > 0:
                return float(self.amount) * recipe.production_time
            return 0.0

        return 0.0

    def __repr__(self):
        return f'<CustomCostItem {self.name}>'
