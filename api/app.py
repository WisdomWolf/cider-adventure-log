from flask import Flask

from .auth import auth_bp, init_oidc
from .cli import register_cli
from .config import get_config
from .extensions import cors, db, login_manager, migrate
from .routes import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    # CORS is not credentialed: the frontend always talks to the API same-origin
    # (via a dev-server proxy locally, nginx in prod), so no cross-origin cookies.
    cors.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    if app.config.get('SSO_ENABLED'):
        init_oidc(app)

    register_cli(app)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
