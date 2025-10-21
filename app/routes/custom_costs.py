from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, CustomCostItem

bp = Blueprint('custom_costs', __name__, url_prefix='/custom-costs')


@bp.route('/')
@login_required
def index():
    """カスタム原価項目一覧"""
    items = CustomCostItem.query.filter_by(store_id=current_user.id)\
        .order_by(CustomCostItem.display_order, CustomCostItem.id)\
        .all()

    return render_template('custom_costs/index.html', items=items)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    """カスタム原価項目の作成"""
    name = request.form.get('name')
    calculation_type = request.form.get('calculation_type')
    amount = request.form.get('amount')
    description = request.form.get('description', '')

    if not name or not calculation_type or not amount:
        flash('必須項目を入力してください', 'danger')
        return redirect(url_for('custom_costs.index'))

    try:
        # 現在の最大表示順序を取得
        max_order = db.session.query(db.func.max(CustomCostItem.display_order))\
            .filter_by(store_id=current_user.id).scalar() or 0

        item = CustomCostItem(
            store_id=current_user.id,
            name=name,
            calculation_type=calculation_type,
            amount=float(amount),
            description=description,
            display_order=max_order + 1
        )

        db.session.add(item)
        db.session.commit()

        flash(f'原価項目「{name}」を追加しました', 'success')
    except ValueError:
        flash('金額は数値で入力してください', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'エラーが発生しました: {str(e)}', 'danger')

    return redirect(url_for('custom_costs.index'))


@bp.route('/<int:id>/update', methods=['POST'])
@login_required
def update(id):
    """カスタム原価項目の更新"""
    item = CustomCostItem.query.filter_by(id=id, store_id=current_user.id).first_or_404()

    name = request.form.get('name')
    calculation_type = request.form.get('calculation_type')
    amount = request.form.get('amount')
    description = request.form.get('description', '')

    if not name or not calculation_type or not amount:
        flash('必須項目を入力してください', 'danger')
        return redirect(url_for('custom_costs.index'))

    try:
        item.name = name
        item.calculation_type = calculation_type
        item.amount = float(amount)
        item.description = description

        db.session.commit()

        flash(f'原価項目「{name}」を更新しました', 'success')
    except ValueError:
        flash('金額は数値で入力してください', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'エラーが発生しました: {str(e)}', 'danger')

    return redirect(url_for('custom_costs.index'))


@bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
def toggle(id):
    """カスタム原価項目の有効/無効切り替え"""
    item = CustomCostItem.query.filter_by(id=id, store_id=current_user.id).first_or_404()

    item.is_active = not item.is_active
    db.session.commit()

    status = '有効' if item.is_active else '無効'
    flash(f'「{item.name}」を{status}にしました', 'info')

    return redirect(url_for('custom_costs.index'))


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """カスタム原価項目の削除"""
    item = CustomCostItem.query.filter_by(id=id, store_id=current_user.id).first_or_404()

    name = item.name
    db.session.delete(item)
    db.session.commit()

    flash(f'原価項目「{name}」を削除しました', 'info')

    return redirect(url_for('custom_costs.index'))


@bp.route('/reorder', methods=['POST'])
@login_required
def reorder():
    """表示順序の変更"""
    order_data = request.json.get('order', [])

    try:
        for index, item_id in enumerate(order_data):
            item = CustomCostItem.query.filter_by(
                id=item_id,
                store_id=current_user.id
            ).first()
            if item:
                item.display_order = index

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
