from flask import Blueprint, redirect, render_template, url_for, request, jsonify, g
from app.db import get_db

bp = Blueprint('catalogue', __name__)


@bp.route('/')
def index_redirect():
    return redirect(url_for('catalogue.catalogue'))



@bp.route('/to_cart', methods=['POST'])
def to_cart():
    if g.user is None:
        return jsonify({
            'status': 'error',
            'message': 'Для добавления товара в корзину необходимо войти в аккаунт'
        }), 401

    data = request.get_json(silent=True) or {}

    try:
        product_id = int(data.get('product_id'))
        size = int(data.get('size'))
        quantity = int(data.get('value'))

        if quantity < 1:
            raise ValueError()

    except (TypeError, ValueError):
        return jsonify({
            'status': 'error',
            'message': 'Некорректные данные товара'
        }), 400

    db = get_db()

    stock = db.execute(
        '''
        SELECT quantity
        FROM product_size
        WHERE product_id = ? AND size = ?
        ''',
        (product_id, size)
    ).fetchone()

    if stock is None or stock['quantity'] < quantity:
        return jsonify({
            'status': 'error',
            'message': 'Недостаточно товара выбранного размера'
        }), 400

    existing = db.execute(
        '''
        SELECT quantity
        FROM cart
        WHERE product_id = ? AND user_id = ? AND size = ?
        ''',
        (product_id, g.user['id'], size)
    ).fetchone()

    new_quantity = quantity

    if existing:
        new_quantity += existing['quantity']

    if new_quantity > stock['quantity']:
        return jsonify({
            'status': 'error',
            'message': 'В корзине получится больше пар, чем есть в наличии'
        }), 400

    if existing:
        db.execute(
            '''
            UPDATE cart
            SET quantity = ?
            WHERE product_id = ? AND user_id = ? AND size = ?
            ''',
            (new_quantity, product_id, g.user['id'], size)
        )
    else:
        db.execute(
            '''
            INSERT INTO cart (product_id, user_id, size, quantity)
            VALUES (?, ?, ?, ?)
            ''',
            (product_id, g.user['id'], size, quantity)
        )

    db.commit()

    return jsonify({'status': 'success'})

@bp.route('/catalogue')
def catalogue():
    """Главная страница с каталогом товаров."""
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '')
    sort_direction = request.args.get('sort_direction', '0')

    db = get_db()

    query = '''
        SELECT
            p.id,
            p.title,
            p.price,
            MAX(COALESCE(p.discount, 0), COALESCE(p.auto_discount, 0)) AS discount,
            p.category,
            p.image,
            p.description,
            COALESCE(SUM(ps.quantity), 0) AS total_stock
        FROM product p
        LEFT JOIN product_size ps ON p.id = ps.product_id
    '''

    conditions = []
    params = []

    if category_filter:
        conditions.append('LOWER(p.category) = LOWER(?)')
        params.append(category_filter)

    if search:
        conditions.append(
            '(LOWER(p.title) LIKE LOWER(?) OR LOWER(p.description) LIKE LOWER(?))'
        )
        search_value = f'%{search}%'
        params.extend([search_value, search_value])

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' GROUP BY p.id'

    if sort_direction == '1':
        query += '''
            ORDER BY p.price * 1 - MAX(COALESCE(p.discount, 0), COALESCE(p.auto_discount, 0)) / 100.0 ASC
        '''
    else:
        query += '''
            ORDER BY p.price * 1 - MAX(COALESCE(p.discount, 0), COALESCE(p.auto_discount, 0)) / 100.0 DESC
        '''

    products = db.execute(query, params).fetchall()

    categories = db.execute(
        'SELECT DISTINCT category FROM product ORDER BY category'
    ).fetchall()

    if g.user:
        carts = db.execute(
            'SELECT product_id FROM cart WHERE user_id = ?',
            (g.user['id'],)
        ).fetchall()
        cart_count = len(carts)
    else:
        carts = [{'product_id': None}]
        cart_count = None

    return render_template(
        'catalogue/catalog.html',
        products=products,
        carts=carts,
        cart_count=cart_count,
        categories=categories,
        search=search,
        category_filter=category_filter,
        sort_direction=sort_direction
    )


@bp.route('/product')
@bp.route('/product/<int:product_id>')
def product(product_id=1):
    db = get_db()

    product = db.execute(
        '''
        SELECT
            id,
            title,
            description,
            price,
            MAX(COALESCE(discount, 0), COALESCE(auto_discount, 0)) AS discount,
            category,
            image,
            manufacturer,
            composition
        FROM product
        WHERE id = ?
        ''',
        (product_id,)
    ).fetchone()

    if product is None:
        return 'Товар не найден', 404

    sizes = db.execute(
        '''
        SELECT size, quantity
        FROM product_size
        WHERE product_id = ?
        ORDER BY size
        ''',
        (product_id,)
    ).fetchall()

    if g.user is not None:
        carts = db.execute(
            'SELECT product_id FROM cart WHERE user_id = ?',
            (g.user['id'],)
        ).fetchall()
        cart_count = len(carts)
    else:
        carts = [{'product_id': None}]
        cart_count = None

    return render_template(
        'catalogue/product.html',
        product=product,
        sizes=sizes,
        carts=carts,
        cart_count=cart_count
    )
