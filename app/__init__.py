from flask import Flask
from flask_login import LoginManager
from app.models import db, Store
import os


def create_app(test_config=None):
    """アプリケーションファクトリ"""
    app = Flask(__name__, instance_relative_config=True)

    # 基本設定
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///bakery.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            'pool_pre_ping': True,
        }
    )

    if test_config:
        app.config.update(test_config)

    # instanceフォルダの確認
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # データベース初期化
    db.init_app(app)

    # ログイン管理
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'ログインが必要です。'

    @login_manager.user_loader
    def load_user(user_id):
        return Store.query.get(int(user_id))

    # ルート登録
    from app.routes import auth, main, ingredients, recipes, labels, custom_costs
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(ingredients.bp)
    app.register_blueprint(recipes.bp)
    app.register_blueprint(labels.bp)
    app.register_blueprint(custom_costs.bp)

    # データベーステーブル作成
    with app.app_context():
        db.create_all()

    return app
