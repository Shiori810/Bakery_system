from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, IntegerField, BooleanField, SelectField, TextAreaField, FieldList, FormField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange, Optional
from app.models import Store


class RegistrationForm(FlaskForm):
    """店舗登録フォーム"""
    login_id = StringField('ログインID', validators=[
        DataRequired(message='ログインIDは必須です'),
        Length(min=4, max=50, message='ログインIDは4〜50文字で入力してください')
    ])
    store_name = StringField('店舗名', validators=[
        DataRequired(message='店舗名は必須です'),
        Length(min=1, max=100, message='店舗名は1〜100文字で入力してください')
    ])
    password = PasswordField('パスワード', validators=[
        DataRequired(message='パスワードは必須です'),
        Length(min=6, message='パスワードは6文字以上で入力してください')
    ])
    confirm_password = PasswordField('パスワード確認', validators=[
        DataRequired(message='パスワード確認は必須です'),
        EqualTo('password', message='パスワードが一致しません')
    ])

    def validate_login_id(self, login_id):
        """ログインIDの重複チェック"""
        store = Store.query.filter_by(login_id=login_id.data).first()
        if store:
            raise ValidationError('このログインIDは既に使用されています')


class LoginForm(FlaskForm):
    """ログインフォーム"""
    login_id = StringField('ログインID', validators=[
        DataRequired(message='ログインIDを入力してください')
    ])
    password = PasswordField('パスワード', validators=[
        DataRequired(message='パスワードを入力してください')
    ])


class IngredientForm(FlaskForm):
    """材料登録・編集フォーム"""
    name = StringField('材料名', validators=[
        DataRequired(message='材料名は必須です'),
        Length(max=100, message='材料名は100文字以内で入力してください')
    ])

    # 購入情報
    purchase_price = DecimalField('購入価格', validators=[
        Optional(),
        NumberRange(min=0, message='購入価格は0以上で入力してください')
    ], places=2)
    purchase_quantity = DecimalField('購入数量', validators=[
        Optional(),
        NumberRange(min=0.001, message='購入数量は0より大きい値で入力してください')
    ], places=3, default=1)
    purchase_unit = SelectField('購入単位', choices=[
        ('', '選択してください'),
        ('kg', 'kg'),
        ('g', 'g'),
        ('L', 'L'),
        ('ml', 'ml'),
        ('個', '個'),
        ('枚', '枚'),
        ('本', '本')
    ], validators=[Optional()])

    # 使用情報
    usage_unit = SelectField('使用単位', choices=[
        ('', '選択してください'),
        ('g', 'g'),
        ('kg', 'kg'),
        ('ml', 'ml'),
        ('L', 'L'),
        ('個', '個'),
        ('枚', '枚'),
        ('本', '本')
    ], validators=[Optional()])

    supplier = StringField('仕入先', validators=[
        Optional(),
        Length(max=100, message='仕入先は100文字以内で入力してください')
    ])
    is_allergen = BooleanField('アレルゲン')
    allergen_type = SelectField('アレルゲン種類', choices=[
        ('', 'なし'),
        ('小麦', '小麦'),
        ('卵', '卵'),
        ('乳', '乳'),
        ('そば', 'そば'),
        ('落花生', '落花生'),
        ('えび', 'えび'),
        ('かに', 'かに'),
        ('その他', 'その他')
    ], validators=[Optional()])


class RecipeIngredientForm(FlaskForm):
    """レシピ材料フォーム(FieldListで使用)"""
    ingredient_id = SelectField('材料', coerce=int, validators=[DataRequired()])
    quantity = DecimalField('使用量', validators=[
        DataRequired(message='使用量は必須です'),
        NumberRange(min=0, message='使用量は0以上で入力してください')
    ], places=3)


class RecipeForm(FlaskForm):
    """レシピ登録・編集フォーム"""
    product_name = StringField('商品名', validators=[
        DataRequired(message='商品名は必須です'),
        Length(max=100, message='商品名は100文字以内で入力してください')
    ])
    category = SelectField('カテゴリー', choices=[
        ('食パン', '食パン'),
        ('菓子パン', '菓子パン'),
        ('調理パン', '調理パン'),
        ('ハード系', 'ハード系'),
        ('デニッシュ', 'デニッシュ'),
        ('その他', 'その他')
    ], validators=[Optional()])
    production_quantity = IntegerField('製造個数', validators=[
        DataRequired(message='製造個数は必須です'),
        NumberRange(min=1, message='製造個数は1以上で入力してください')
    ], default=1)
    production_time = IntegerField('製造時間(分)', validators=[
        Optional(),
        NumberRange(min=0, message='製造時間は0以上で入力してください')
    ], default=0)
    shelf_life_days = IntegerField('賞味期限(日数)', validators=[
        Optional(),
        NumberRange(min=0, message='賞味期限は0以上で入力してください')
    ])
    custom_profit_margin = DecimalField('商品ごとの利益率(%)', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='利益率は0〜100で入力してください')
    ], places=2)
    selling_price = DecimalField('販売価格(円)', validators=[
        Optional(),
        NumberRange(min=0, message='販売価格は0以上で入力してください')
    ], places=2)


class CostSettingForm(FlaskForm):
    """原価計算設定フォーム"""
    include_labor_cost = BooleanField('人件費を含める')
    include_utility_cost = BooleanField('光熱費を含める')
    hourly_wage = DecimalField('時給(円)', validators=[
        Optional(),
        NumberRange(min=0, message='時給は0以上で入力してください')
    ], places=2, default=0)
    monthly_utility_cost = DecimalField('月額光熱費(円)', validators=[
        Optional(),
        NumberRange(min=0, message='月額光熱費は0以上で入力してください')
    ], places=2, default=0)
    profit_margin = DecimalField('利益率(%)', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='利益率は0〜100で入力してください')
    ], places=2, default=30)


class PasswordChangeForm(FlaskForm):
    """パスワード変更フォーム"""
    current_password = PasswordField('現在のパスワード', validators=[
        DataRequired(message='現在のパスワードを入力してください')
    ])
    new_password = PasswordField('新しいパスワード', validators=[
        DataRequired(message='新しいパスワードを入力してください'),
        Length(min=6, message='パスワードは6文字以上で入力してください')
    ])
    confirm_password = PasswordField('新しいパスワード確認', validators=[
        DataRequired(message='新しいパスワード確認を入力してください'),
        EqualTo('new_password', message='パスワードが一致しません')
    ])


class PasswordResetForm(FlaskForm):
    """パスワードリセットフォーム（ログインID確認用）"""
    login_id = StringField('ログインID', validators=[
        DataRequired(message='ログインIDを入力してください')
    ])
    new_password = PasswordField('新しいパスワード', validators=[
        DataRequired(message='新しいパスワードを入力してください'),
        Length(min=6, message='パスワードは6文字以上で入力してください')
    ])
    confirm_password = PasswordField('新しいパスワード確認', validators=[
        DataRequired(message='新しいパスワード確認を入力してください'),
        EqualTo('new_password', message='パスワードが一致しません')
    ])


class ForgotLoginIDForm(FlaskForm):
    """ログインID確認フォーム"""
    store_name = StringField('店舗名', validators=[
        DataRequired(message='店舗名を入力してください')
    ])
