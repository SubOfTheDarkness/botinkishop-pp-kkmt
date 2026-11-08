import sqlite3
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.execute('PRAGMA foreign_keys = ON')
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()  

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        db.commit()

def update_auto_discounts():
    db = get_db()

    db.execute(
        '''
        UPDATE product
        SET auto_discount = CASE
            WHEN EXISTS (
                SELECT 1
                FROM order_products op
                JOIN orders o ON o.id = op.order_id
                WHERE op.product_id = product.id
                  AND date(o.created_at) >= date(
                      'now', 'localtime', 'start of month', '-1 month'
                  )
                  AND date(o.created_at) < date(
                      'now', 'localtime', 'start of month'
                  )
            )
            THEN 0
            ELSE 25
        END
        '''
    )

    db.commit()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)    