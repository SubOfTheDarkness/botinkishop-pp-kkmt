DROP TABLE IF EXISTS order_products;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS product_size;
DROP TABLE IF EXISTS product;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    flag_admin INTEGER(1) NOT NULL DEFAULT 0
);

CREATE TABLE cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    size INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);
CREATE TABLE product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    discount INTEGER DEFAULT 0,
    auto_discount INTEGER NOT NULL DEFAULT 0,
    category TEXT,
    image TEXT,
    manufacturer TEXT,
    composition TEXT
);
CREATE TABLE product_size (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    size INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
    UNIQUE (product_id, size)
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone_number TEXT,
    user_id INTEGER NOT NULL,
    email TEXT NOT NULL,
    address_delivery TEXT,
    pay_method INTEGER(1) NOT NULL DEFAULT(0),
    comment TEXT,
    status TEXT NOT NULL DEFAULT 'Новый',
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES user (id)
);
CREATE TABLE order_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    size INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE RESTRICT,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE RESTRICT
);

INSERT INTO product (
    title, description, price, discount, category, image,
    manufacturer, composition
) VALUES
(
    'Ботинки',
    'Ботинки крутые зимние',
    4000,
    30,
    'Ботинки',
    '/static/images/boots.jpg',
    'Botinki Shop',
    'Натуральная кожа, мех, резиновая подошва'
),
(
    'Кроссовки',
    'Удобные повседневные кроссовки для прогулок и активного отдыха',
    3500,
    10,
    'Кроссовки',
    '/static/images/sneakers.jpg',
    'Botinki Shop',
    'Текстиль, искусственная кожа, резиновая подошва'
);

INSERT INTO product_size (product_id, size, quantity) VALUES
(1, 36, 2),
(1, 37, 4),
(1, 38, 6),
(1, 39, 8),
(1, 40, 5),
(1, 41, 3),
(1, 42, 2),
(1, 43, 1),
(1, 44, 0),
(1, 45, 0),
(2, 38, 2),
(2, 39, 4),
(2, 40, 6),
(2, 41, 5),
(2, 42, 3),
(2, 43, 2);

INSERT INTO user(email, flag_admin) VALUES
('admin', 1);