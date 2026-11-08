DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_products;
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    flag_admin INTEGER(1) NOT NULL DEFAULT 0
);

CREATE TABLE cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (user_id) REFERENCES user (id)
);
CREATE TABLE product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    discount INTEGER DEFAULT 0,
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
    FOREIGN KEY (user_id) REFERENCES user (id)
);
CREATE TABLE order_products(
    order_id INTEGER NOT NULL,
    product TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,
    PRIMARY KEY(order_id,product),
    FOREIGN KEY (order_id) REFERENCES orders (id)
);

INSERT INTO product (
    title, description, price, discount, category, image,
    manufacturer, composition
) VALUES (
    'Ботинки',
    'Ботинки крутые зимние',
    4000,
    15,
    'Обувь',
    '/static/images/boots.jpg',
    'Botinki Shop',
    'Натуральная кожа, мех, резиновая подошва'
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
(1, 45, 0);

INSERT INTO user(email, flag_admin) VALUES
('admin', 1);