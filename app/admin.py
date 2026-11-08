from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, g
from app.auth import admin_required
from app.db import get_db

bp = Blueprint('admin', __name__)


@bp.route('/admin')
@admin_required
def admin():
    import os
    db = get_db()
    products = db.execute('SELECT * FROM product ORDER BY id DESC').fetchall()
    users = db.execute('SELECT * FROM user ORDER BY id DESC').fetchall()
    carts = db.execute(
        'SELECT c.id, u.email, p.title, c.quantity, c.user_id, c.product_id '
        'FROM cart c '
        'LEFT JOIN user u ON u.id = c.user_id '
        'LEFT JOIN product p ON p.id = c.product_id '
        'ORDER BY c.id DESC'
    ).fetchall()
    orders = db.execute(
        'SELECT o.id, o.name, o.phone_number, o.email, o.address_delivery, '
        'o.pay_method, o.comment, '
        "GROUP_CONCAT(op.product || ' x' || op.quantity, ', ') AS products, "
        'SUM(op.price * op.quantity) AS total '
        'FROM orders o '
        'LEFT JOIN order_products op ON op.order_id = o.id '
        'GROUP BY o.id '
        'ORDER BY o.id DESC'
    ).fetchall()
    images = []
    img_dir = os.path.join(current_app.root_path, 'static', 'images')
    if os.path.exists(img_dir):
        images = [f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.png', '.jpeg', '.gif', '.webp'))]
    
    tab = request.args.get('tab', 'products')

    return render_template('admin/admin.html', products=products, users=users, carts=carts, images=images, active_tab=tab, orders=orders)


# ========== ТОВАРЫ ==========

@bp.route('/admin/product/add', methods=['POST'])
@admin_required
def add_product():
    title = request.form['title']
    description = request.form['description']
    price = request.form['price']
    discount = request.form.get('discount', 0) or 0
    category = request.form['category']
    image = request.form.get('image', '')
    image_url = request.form.get('image_url', '')

    if image_url:
        image = image_url

    db = get_db()
    db.execute(
        'INSERT INTO product(title, description, price, discount, category, image) VALUES(?,?,?,?,?,?)',
        (title, description, price, discount, category, image)
    )
    db.commit()
    flash('Товар добавлен', 'success')
    return redirect(url_for('admin.admin', tab='products'))


@bp.route('/admin/product/edit/<int:product_id>', methods=['POST'])
@admin_required
def edit_product(product_id):
    title = request.form['title']
    description = request.form['description']
    price = request.form['price']
    discount = request.form.get('discount', 0) or 0
    category = request.form['category']
    image = request.form.get('image', '')
    db = get_db()
    db.execute(
        'UPDATE product SET title=?, description=?, price=?, discount=?, category=?, image=? WHERE id=?',
        (title, description, price, discount, category, image, product_id)
    )
    db.commit()
    flash('Товар обновлён', 'success')
    return redirect(url_for('admin.admin', tab='products'))


@bp.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    db = get_db()
    db.execute('DELETE FROM cart WHERE product_id = ?', (product_id,))
    db.execute('DELETE FROM product WHERE id = ?', (product_id,))
    db.commit()
    flash('Товар удалён', 'success')
    return redirect(url_for('admin.admin', tab='products'))


# ========== ПОЛЬЗОВАТЕЛИ ==========

@bp.route('/admin/user/add', methods=['POST'])
@admin_required
def add_user():
    login = request.form['email'].strip()
    db = get_db()

    try:
        db.execute(
            'INSERT INTO user(email) VALUES(?)',
            (login,)
        )
        db.commit()
        flash('Пользователь добавлен', 'success')
    except db.IntegrityError:
        flash('Пользователь уже существует', 'error')

    return redirect(url_for('admin.admin', tab='users'))

@bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    error = None
    if user_id != g.user['id']:
        if user_id == 1:
            error = 'Нельзя удалять Гл.Админа'
        else:
            db = get_db()
            db.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
            db.execute('DELETE FROM user WHERE id = ?', (user_id,))
            db.commit()
            flash('Пользователь удалён', 'success')
    else:
        error = 'Нельзя удалять текущего пользователя'
    flash(error, 'error')
    return redirect(url_for('admin.admin', tab='users'))

# ========== КОРЗИНЫ ==========

@bp.route('/admin/cart/delete/<int:cart_id>', methods=['POST'])
@admin_required
def delete_cart_item(cart_id):
    db = get_db()
    db.execute('DELETE FROM cart WHERE id = ?', (cart_id,))
    db.commit()
    flash('Запись удалена', 'success')
    return redirect(url_for('admin.admin', tab='carts'))


@bp.route('/admin/cart/update/<int:cart_id>', methods=['POST'])
@admin_required
def update_cart_item(cart_id):
    quantity = request.form.get('quantity', 1)
    db = get_db()
    db.execute('UPDATE cart SET quantity = ? WHERE id = ?', (quantity, cart_id))
    db.commit()
    flash('Количество обновлено', 'success')
    return redirect(url_for('admin.admin', tab='carts'))

@bp.route('/admin/order/delete/<int:order_id>', methods=['POST'])
@admin_required
def delete_order(order_id):
    db = get_db()
    db.execute('DELETE FROM order_products WHERE order_id = ?', (order_id,))
    db.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    db.commit()
    flash('Заказ удалён', 'success')
    return redirect(url_for('admin.admin', tab='orders'))
