import flask
import os
from app.db import get_db

def create_app():
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'botinki_shop.sqlite')
    )
    app.config.from_pyfile('config.py')
    os.makedirs(app.instance_path, exist_ok=True)
    
    from . import db
    db.init_app(app)
    from . import cart
    app.register_blueprint(cart.bp)
    from . import admin
    app.register_blueprint(admin.bp)
    from . import auth
    app.register_blueprint(auth.bp)

    from . import catalogue
    app.register_blueprint(catalogue.bp)
    
    @app.errorhandler(404)
    def not_found(error):
        return '<h1>Ошибка 404</h1><p><a href="/">Вернуться на главную страницу</a></p>', 404
    
    @app.errorhandler(500)
    def server_error(error):
        return '<h1>Ошибка 500(ошибка сервера)</h1><p><a href="/">Вернуться на главную страницу</a></p>', 500
    
    return app