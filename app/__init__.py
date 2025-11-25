from flask import Flask
from flask_login import LoginManager
from app.models import db, Store
import os


def create_app(test_config=None):
    """アプリケーションファクトリ"""
    app = Flask(__name__, instance_relative_config=True)

    # 基本設定
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///bakery.db')

    # RenderのPostgreSQLは postgres:// で始まるが、SQLAlchemyは postgresql:// が必要
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=database_url,
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

    # エラーハンドラー
    @app.errorhandler(500)
    def internal_error(error):
        import traceback
        print("[ERROR] Internal Server Error:")
        print(traceback.format_exc())
        db.session.rollback()
        return "Internal Server Error - Please check the logs", 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        print(f"[ERROR] Unhandled exception: {e}")
        print(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

    # データベーステーブル作成
    with app.app_context():
        db.create_all()

    return app
