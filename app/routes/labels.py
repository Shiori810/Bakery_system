from flask import Blueprint, render_template, send_file, request
from flask_login import login_required, current_user
from app.models import Recipe, CostSetting
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from datetime import datetime, timedelta
import io
import os

bp = Blueprint('labels', __name__, url_prefix='/labels')


def register_fonts():
    """日本語フォントの登録"""
    try:
        # Windows標準フォント
        font_path = 'C:/Windows/Fonts/msgothic.ttc'
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Japanese', font_path))
            return 'Japanese'
    except:
        pass

    # フォントが見つからない場合はHelveticaを使用
    return 'Helvetica'


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


@bp.route('/<int:id>/generate', methods=['POST'])
@login_required
def generate(id):
    """ラベルPDF生成"""
    recipe = Recipe.query.filter_by(id=id, store_id=current_user.id).first_or_404()
    cost_setting = CostSetting.query.filter_by(store_id=current_user.id).first()

    # オプションの取得
    show_cost = request.form.get('show_cost') == 'on'
    show_price = request.form.get('show_price') == 'on'
    production_date = request.form.get('production_date', datetime.now().strftime('%Y-%m-%d'))
    label_count = int(request.form.get('label_count', 1))

    # PDF生成
    buffer = io.BytesIO()
    font_name = register_fonts()

    # A4サイズ (210mm x 297mm)
    page_width, page_height = A4

    # ラベルサイズ (90mm x 60mm)
    label_width = 90 * mm
    label_height = 60 * mm

    # 1ページに並べるラベル数 (2列 x 4行 = 8枚)
    cols = 2
    rows = 4
    margin_left = 15 * mm
    margin_top = 20 * mm
    gap_x = 10 * mm
    gap_y = 8 * mm

    c = canvas.Canvas(buffer, pagesize=A4)

    labels_drawn = 0
    for i in range(label_count):
        if labels_drawn > 0 and labels_drawn % (cols * rows) == 0:
            c.showPage()

        col = (labels_drawn % (cols * rows)) % cols
        row = (labels_drawn % (cols * rows)) // cols

        x = margin_left + col * (label_width + gap_x)
        y = page_height - margin_top - (row + 1) * label_height - row * gap_y

        # ラベル描画
        draw_label(c, x, y, label_width, label_height, recipe, cost_setting,
                  show_cost, show_price, production_date, font_name)

        labels_drawn += 1

    c.save()
    buffer.seek(0)

    # ファイル名
    filename = f"label_{recipe.product_name}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return send_file(buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=filename)


def draw_label(c, x, y, width, height, recipe, cost_setting,
              show_cost, show_price, production_date, font_name):
    """ラベルを描画"""
    # 枠線
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)
    c.rect(x, y, width, height)

    padding = 3 * mm
    current_y = y + height - padding

    # 商品名 (大きめ)
    c.setFont(font_name, 14)
    text_width = c.stringWidth(recipe.product_name, font_name, 14)
    if text_width > width - 2 * padding:
        # 長い場合は折り返し
        lines = simpleSplit(recipe.product_name, font_name, 14, width - 2 * padding)
        for line in lines:
            c.drawString(x + padding, current_y - 5 * mm, line)
            current_y -= 6 * mm
    else:
        c.drawString(x + padding, current_y - 5 * mm, recipe.product_name)
        current_y -= 8 * mm

    # 区切り線
    c.setLineWidth(0.3)
    c.line(x + padding, current_y, x + width - padding, current_y)
    current_y -= 4 * mm

    # 材料一覧
    c.setFont(font_name, 8)
    c.drawString(x + padding, current_y, "【材料】")
    current_y -= 3.5 * mm

    ingredients_text = "、".join([ri.ingredient.name for ri in recipe.recipe_ingredients])
    if not ingredients_text:
        ingredients_text = "材料未設定"

    # 材料名を折り返し
    lines = simpleSplit(ingredients_text, font_name, 7, width - 2 * padding)
    c.setFont(font_name, 7)
    for line in lines[:4]:  # 最大4行
        c.drawString(x + padding, current_y, line)
        current_y -= 3 * mm

    current_y -= 2 * mm

    # アレルゲン情報
    allergens = recipe.get_allergens()
    if allergens:
        c.setFont(font_name, 7)
        allergen_text = f"アレルゲン: {', '.join(allergens)}"
        c.drawString(x + padding, current_y, allergen_text)
        current_y -= 4 * mm

    # 製造日・賞味期限
    c.setFont(font_name, 7)
    prod_date = datetime.strptime(production_date, '%Y-%m-%d')
    c.drawString(x + padding, current_y, f"製造日: {prod_date.strftime('%Y年%m月%d日')}")
    current_y -= 3 * mm

    if recipe.shelf_life_days:
        exp_date = prod_date + timedelta(days=recipe.shelf_life_days)
        c.drawString(x + padding, current_y, f"賞味期限: {exp_date.strftime('%Y年%m月%d日')}")
        current_y -= 3 * mm

    # 原価・価格情報
    if show_cost or show_price:
        current_y -= 1 * mm
        c.setLineWidth(0.3)
        c.line(x + padding, current_y, x + width - padding, current_y)
        current_y -= 3 * mm

    if show_cost:
        unit_cost = recipe.calculate_unit_cost(cost_setting)
        c.drawString(x + padding, current_y, f"原価: {unit_cost:.0f}円")
        current_y -= 3 * mm

    if show_price:
        suggested_price = recipe.calculate_suggested_price(cost_setting) if cost_setting else 0
        c.drawString(x + padding, current_y, f"販売価格: {suggested_price:.0f}円")
        current_y -= 3 * mm

    # 店舗名(右下)
    c.setFont(font_name, 6)
    store_name = recipe.store.store_name
    text_width = c.stringWidth(store_name, font_name, 6)
    c.drawString(x + width - padding - text_width, y + padding, store_name)
