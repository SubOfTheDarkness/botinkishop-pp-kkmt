from flask import Blueprint, render_template, request, jsonify, g, redirect, url_for,flash
from app.db import get_db
from app.auth import login_required

bp = Blueprint('cart', __name__)

@bp.route('/update_count', methods=['POST'])
def update_count():
    data = request.get_json()
    val = data.get('value')
    item_ids = data.get('item_id')
    try:
        db = get_db()
        db.execute(
            'UPDATE cart'
            ' SET quantity=?'
            ' WHERE id=?', (val,item_ids))
        db.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error','message': str(e)})

@bp.route('/delete_product', methods=['POST'])
def delete_product():
    data = request.get_json()
    item_ids = data.get('item_id')
    try:
        db = get_db()
        db.execute(
            'DELETE FROM cart'
            ' WHERE id=?', (int(item_ids),))
        db.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error','message': str(e)})

@bp.route('/clear', methods=['POST'])
def clear():
    error=None
    try:
        db = get_db()
        db.execute(
            'DELETE FROM cart'
            ' WHERE user_id=?', (g.user['id'],))
        db.commit()
    except Exception as e:
        error=e
    flash(error, 'error')
    return redirect(url_for('cart.cart'))

@bp.route('/cart')
@login_required
def cart():
    """Страница корзины."""
    db = get_db()
    cart_items = db.execute(
        'SELECT c.id AS item_id,c.product_id, p.title, p.price*(1-p.discount/100.0) AS price, c.quantity, p.category, p.image'
        ' FROM cart c'
        ' JOIN product p ON p.id = c.product_id'
        ' WHERE c.user_id=?', (g.user['id'],)
    ).fetchall()
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    cart_count = len(cart_items)
    return render_template('cart/cart.html', cart_items=cart_items, total=total, cart_count=cart_count)


@bp.route('/checkout')
@login_required
def checkout():
    """Страница оформления заказа."""
    db = get_db()
    cart_summary = db.execute(
        'SELECT p.id,p.title, c.quantity, p.price*(1-p.discount/100.0) AS subtotal'
        ' FROM cart c'
        ' JOIN product p ON p.id = c.product_id'
        ' WHERE c.user_id=?', (g.user['id'],)
    ).fetchall()
    total = sum(item['subtotal'] * item['quantity'] for item in cart_summary)
    cart_count = len(cart_summary)
    return render_template('cart/checkout.html', cart_summary=cart_summary, total=total, cart_count=cart_count)


@bp.route('/create_order', methods=['POST'])
@login_required
def create_order():
    name = request.form['name']
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    address = request.form.get('city', '') + ', ' + request.form.get('address', '') 
    pay_method = 1 if request.form.get('payment') == 'card' else 0
    comment = request.form.get('comment', '')

    db = get_db()

    cart_items = db.execute(
        'SELECT p.title, p.price*(1-p.discount/100.0) AS price, c.quantity'
        ' FROM cart c'
        ' JOIN product p ON p.id = c.product_id'
        ' WHERE c.user_id=?', (g.user['id'],)
    ).fetchall()

    if not cart_items:
        return redirect(url_for('cart.cart'))

    cursor = db.execute(
        'INSERT INTO orders(name, phone_number, user_id, email, address_delivery, pay_method, comment)'
        ' VALUES(?,?,?,?,?,?,?)',
        (name, phone, g.user['id'], email, address, pay_method, comment)
    )
    order_id = cursor.lastrowid

    for item in cart_items:
        db.execute(
            'INSERT INTO order_products(order_id, product, quantity, price) VALUES(?,?,?,?)',
            (order_id, item['title'], item['quantity'], item['price'])
        )

    db.execute('DELETE FROM cart WHERE user_id=?', (g.user['id'],))
    db.commit()

    return redirect(url_for('cart.orders'))


@bp.route('/orders')
@login_required
def orders():
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
    for order in user_orders:
        items = db.execute(
            'SELECT product, quantity, price FROM order_products WHERE order_id=?',
            (order['id'],)
        ).fetchall()
        total = sum(item['price'] * item['quantity'] for item in items)
        orders_with_items.append({
            'order': order,
            'products': items,
            'total': total
        })

    return render_template('cart/orders.html', orders=orders_with_items)