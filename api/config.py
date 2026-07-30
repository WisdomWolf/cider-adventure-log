import os


def _bool_env(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('FLASK_DB_URI', 'sqlite:///products.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = _bool_env('FLASK_DEBUG')
    SESSION_COOKIE_SECURE = False

    AUTHENTIK_ISSUER = os.environ.get('AUTHENTIK_ISSUER')
    AUTHENTIK_CLIENT_ID = os.environ.get('AUTHENTIK_CLIENT_ID')
    AUTHENTIK_CLIENT_SECRET = os.environ.get('AUTHENTIK_CLIENT_SECRET')
    AUTHENTIK_AUTO_PROVISION_GROUP = os.environ.get('AUTHENTIK_AUTO_PROVISION_GROUP')
    OIDC_REDIRECT_URI = os.environ.get('AUTHENTIK_REDIRECT_URI')

    SSO_ENABLED = bool(
        AUTHENTIK_ISSUER and AUTHENTIK_CLIENT_ID and AUTHENTIK_CLIENT_SECRET and OIDC_REDIRECT_URI
    )


class DevelopmentConfig(BaseConfig):
    ENV_NAME = 'development'
    SECRET_KEY = BaseConfig.SECRET_KEY or 'dev-secret-key-change-me'


class ProductionConfig(BaseConfig):
    ENV_NAME = 'production'
    SESSION_COOKIE_SECURE = True


CONFIG_BY_NAME = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}


def get_config():
    """Select the config class for APP_ENV, failing fast on missing prod requirements."""
    app_env = os.environ.get('APP_ENV', 'development')
    config_class = CONFIG_BY_NAME.get(app_env, DevelopmentConfig)

    if app_env == 'production':
        missing = [name for name in ('SECRET_KEY', 'FLASK_DB_URI') if not os.environ.get(name)]
        if missing:
            raise RuntimeError(
                f"Missing required environment variable(s) for production: {', '.join(missing)}"
            )

    return config_class
