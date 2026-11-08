
import functools

from flask import (
    Blueprint, g, redirect, render_template,
    request, session, url_for, flash
)

from app.db import get_db


bp = Blueprint('auth', __name__)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.auth'))
        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user or not g.user['flag_admin']:
            return redirect(url_for('auth.need_admin'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        login = request.form.get('login', '').strip()

        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE email = ?',
            (login,)
        ).fetchone()

        if user is None:
            flash('Пользователь не найден', 'error')
        else:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('catalogue.catalogue'))

    return render_template('auth/auth.html')


@bp.route('/need_admin')
def need_admin():
    return render_template('auth/need_admin.html')


@bp.route('/profile')
@login_required
def profile():
    db = get_db()

    user_orders = db.execute(
        'SELECT o.id, o.name, o.phone_number, o.email, o.address_delivery,'
        ' o.pay_method, o.comment'
        ' FROM orders o'
        ' WHERE o.user_id = ?'
        ' ORDER BY o.id DESC',
        (g.user['id'],)
    ).fetchall()

    orders_with_items = []
    total_spent = 0

    for order in user_orders:
        items = db.execute(
            'SELECT product, quantity, price FROM order_products WHERE order_id=?',
            (order['id'],)
        ).fetchall()

        total = sum(item['price'] * item['quantity'] for item in items)
        total_spent += total

        orders_with_items.append({
            'order': order,
            'products': items,
            'total': total
        })

    last_order = orders_with_items[0] if orders_with_items else None

    return render_template(
        'auth/profile.html',
        orders=orders_with_items,
        last_order=last_order,
        total_spent=total_spent
    )


@bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user_id = g.user['id']
    db = get_db()

    db.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    db.execute(
        'DELETE FROM order_products WHERE order_id IN '
        '(SELECT id FROM orders WHERE user_id = ?)',
        (user_id,)
    )
    db.execute('DELETE FROM orders WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM user WHERE id = ?', (user_id,))
    db.commit()

    session.clear()
    flash('Аккаунт удалён', 'info')
    return redirect(url_for('catalogue.catalogue'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('catalogue.catalogue'))
