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

# A-ONE製品ラベルサイズプリセット
LABEL_PRESETS = {
    'custom': {
        'name': 'カスタムサイズ',
        'width': 90,
        'height': 60,
        'cols': 2,
        'rows': 4,
        'margin_left': 15,
        'margin_top': 20,
        'gap_x': 10,
        'gap_y': 8
    },
    '31531': {
        'name': 'A-ONE 31531 (12面)',
        'product_code': '31531',
        'width': 86.4,
        'height': 42.3,
        'cols': 2,
        'rows': 6,
        'margin_left': 11.5,
        'margin_top': 21.0,
        'gap_x': 5.1,
        'gap_y': 0
    },
    '72210': {
        'name': 'A-ONE 72210 (10面)',
        'product_code': '72210',
        'width': 86.4,
        'height': 50.8,
        'cols': 2,
        'rows': 5,
        'margin_left': 11.5,
        'margin_top': 21.5,
        'gap_x': 5.1,
        'gap_y': 0
    },
    '31538': {
        'name': 'A-ONE 31538 (21面)',
        'product_code': '31538',
        'width': 70.0,
        'height': 42.3,
        'cols': 3,
        'rows': 7,
        'margin_left': 0,  # 余白なし用紙
        'margin_top': 0,   # 余白なし用紙
        'gap_x': 0,
        'gap_y': 0
    },
    '28918': {
        'name': 'A-ONE 28918 (8面)',
        'product_code': '28918',
        'width': 99.0,
        'height': 67.5,
        'cols': 2,
        'rows': 4,
        'margin_left': 6.0,
        'margin_top': 21.0,
        'gap_x': 0,
        'gap_y': 0
    },
    '28729': {
        'name': 'A-ONE 28729 (18面)',
        'product_code': '28729',
        'width': 63.5,
        'height': 46.6,
        'cols': 3,
        'rows': 6,
        'margin_left': 4.0,
        'margin_top': 21.0,
        'gap_x': 0,
        'gap_y': 0
    },
    '28315': {
        'name': 'A-ONE 28315 (24面)',
        'product_code': '28315',
        'width': 66.0,
        'height': 33.9,
        'cols': 3,
        'rows': 8,
        'margin_left': 4.0,
        'margin_top': 21.5,
        'gap_x': 0,
        'gap_y': 0
    },
    '28765': {
        'name': 'A-ONE 28765 (65面)',
        'product_code': '28765',
        'width': 38.1,
        'height': 21.2,
        'cols': 5,
        'rows': 13,
        'margin_left': 4.0,
        'margin_top': 21.5,
        'gap_x': 0,
        'gap_y': 0
    }
}


def register_fonts():
    """日本語フォントの登録"""
    # Windowsで利用可能な日本語フォントを順に試す
    font_candidates = [
        ('C:/Windows/Fonts/msgothic.ttc', 0),  # MSゴシック（TTCの0番目）
        ('C:/Windows/Fonts/msmincho.ttc', 0),  # MS明朝（TTCの0番目）
        ('C:/Windows/Fonts/meiryo.ttc', 0),    # メイリオ（TTCの0番目）
        ('C:/Windows/Fonts/msgothic.ttc', None),  # MSゴシック（TTC全体）
        ('C:/Windows/Fonts/YuGothM.ttc', 0),   # 游ゴシック Medium
        ('C:/Windows/Fonts/YuGothB.ttc', 0),   # 游ゴシック Bold
    ]

    for font_path, subfont_index in font_candidates:
        try:
            if os.path.exists(font_path):
                if subfont_index is not None:
                    # TTCファイルの特定のサブフォントを指定
                    pdfmetrics.registerFont(TTFont('Japanese', font_path, subfontIndex=subfont_index))
                    print(f"[Font] Successfully registered: {font_path} (subfontIndex={subfont_index})")
                else:
                    # 通常のTTFまたはTTC全体
                    pdfmetrics.registerFont(TTFont('Japanese', font_path))
                    print(f"[Font] Successfully registered: {font_path}")
                return 'Japanese'
        except Exception as e:
            # このフォントが使えない場合は次を試す
            print(f"[Font] Failed to register {font_path}: {e}")
            continue

    # すべてのフォントが使えない場合はHelveticaを使用（文字化けする）
    print("[Font] WARNING: No Japanese font available, using Helvetica (text will be garbled)")
    return 'Helvetica'


@bp.route('/<int:id>')
@login_required
def preview(id):
    """ラベルプレビュー"""
    recipe = Recipe.query.filter_by(id=id, store_id=current_user.id).first_or_404()
    cost_setting = CostSetting.query.filter_by(store_id=current_user.id).first()

    # 原価情報
    unit_cost = recipe.calculate_unit_cost(cost_setting)
    suggested_price = recipe.get_selling_price(cost_setting) if cost_setting else unit_cost

    return render_template('labels/preview.html',
                         recipe=recipe,
                         cost_setting=cost_setting,
                         unit_cost=unit_cost,
                         suggested_price=suggested_price,
                         label_presets=LABEL_PRESETS)


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

    # ラベルサイズ設定の取得
    label_preset = request.form.get('label_preset', 'custom')

    # プリセットまたはカスタムサイズの取得
    if label_preset == 'custom':
        # カスタムサイズ
        label_width = float(request.form.get('custom_width', 90)) * mm
        label_height = float(request.form.get('custom_height', 60)) * mm
        cols = int(request.form.get('custom_cols', 2))
        rows = int(request.form.get('custom_rows', 4))
        margin_left = float(request.form.get('custom_margin_left', 15)) * mm
        margin_top = float(request.form.get('custom_margin_top', 20)) * mm
        gap_x = float(request.form.get('custom_gap_x', 10)) * mm
        gap_y = float(request.form.get('custom_gap_y', 8)) * mm
    else:
        # プリセット使用
        preset = LABEL_PRESETS.get(label_preset, LABEL_PRESETS['custom'])
        label_width = preset['width'] * mm
        label_height = preset['height'] * mm
        cols = preset['cols']
        rows = preset['rows']
        margin_left = preset['margin_left'] * mm
        margin_top = preset['margin_top'] * mm
        gap_x = preset['gap_x'] * mm
        gap_y = preset['gap_y'] * mm

    # PDF生成
    buffer = io.BytesIO()
    font_name = register_fonts()

    # A4サイズ (210mm x 297mm)
    page_width, page_height = A4

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
        selling_price = recipe.get_selling_price(cost_setting) if cost_setting else 0
        c.drawString(x + padding, current_y, f"販売価格: {selling_price:.0f}円")
        current_y -= 3 * mm

    # 店舗名(右下)
    c.setFont(font_name, 6)
    store_name = recipe.store.store_name
    text_width = c.stringWidth(store_name, font_name, 6)

    # ラベルの幅を超えないように調整
    max_width = width - 2 * padding
    if text_width > max_width:
        # 店舗名が長い場合は切り詰める
        while text_width > max_width and len(store_name) > 1:
            store_name = store_name[:-1]
            text_width = c.stringWidth(store_name + "...", font_name, 6)
        store_name = store_name + "..."
        text_width = c.stringWidth(store_name, font_name, 6)

    # 右端から余白を確保して描画
    c.drawString(x + width - padding - text_width, y + padding + 1*mm, store_name)
