from flask import Blueprint, redirect, render_template, url_for, request, jsonify, g, flash
from app.auth import login_required
from app.db import get_db

bp = Blueprint('catalogue', __name__)


@bp.route('/')
def index_redirect():
    return redirect(url_for('catalogue.catalogue'))


@bp.route('/to_cart', methods=['POST'])
def to_cart():
    if g.user is not None:
        data = request.get_json()
        val = data.get('value')
        product_ids = data.get('product_id')
        try:
            db = get_db()
            db.execute(
                'INSERT INTO cart(product_id,user_id,quantity)'
                ' VALUES(?,?,?)', (product_ids, g.user['id'], val))
            db.commit()
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        return jsonify({'status': 'error', 'message': 'Для добавления товара в корзину необходимо войти в аккаунт'})


@bp.route('/catalogue')
def catalogue():
    """Главная страница с каталогом товаров."""
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    sort_direction = request.args.get('sort_direction', '0')

    db = get_db()

    # Получаем все товары
    query = 'SELECT id, title, price, discount, category, description, image FROM product'
    params = []
    conditions = []

    if category_filter:
        conditions.append('LOWER(category) = LOWER(?)')
        params.append(category_filter)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    if sort_direction == '1':
        query += ' ORDER BY price * (1 - COALESCE(discount, 0)/100.0) ASC'
    else:
        query += ' ORDER BY price * (1 - COALESCE(discount, 0)/100.0) DESC'

    products = db.execute(query, params).fetchall()

    # Поиск по названию и описанию через питон(игнорит регистр)
    if search:
        search_lower = search.lower()
        products = [
            p for p in products
            if search_lower in p['title'].lower()
            or search_lower in (p['description'] or '').lower()
        ]

    categories = db.execute('SELECT DISTINCT category FROM product ORDER BY category').fetchall()

    if g.user:
        carts = db.execute(
            'SELECT product_id FROM cart WHERE user_id = ?', (g.user['id'],)
        ).fetchall()
        cart_count = len(carts)
    else:
        carts = [{"product_id": None}]
        cart_count = None

    return render_template('catalogue/catalog.html',
                           products=products,
                           carts=carts,
                           cart_count=cart_count,
                           categories=categories,
                           search=search,
                           category_filter=category_filter,
                           sort_direction=sort_direction)


@bp.route('/product')
@bp.route('/product/<int:product_id>')
def product(product_id=1):
    db = get_db()
    product = db.execute(
        'SELECT id, title, description, price, discount, category, image'
        ' FROM product WHERE id = ?', (product_id,)
    ).fetchone()
    if product is None:
        return 'Товар не найден', 404
    if g.user is not None:
        carts = db.execute(
            'SELECT product_id FROM cart WHERE user_id = ?', (g.user['id'],)
        ).fetchall()
        cart_count = len(carts)
    else:
        carts = [{"product_id": None}]
        cart_count = None
    return render_template('catalogue/product.html', product=product, carts=carts, cart_count=cart_count)