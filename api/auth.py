import flask
from flask import Blueprint, current_app, jsonify, redirect, request
from flask_login import current_user, login_required, login_user, logout_user
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ClientMetadata, ProviderConfiguration
from flask_pyoidc.user_session import UserSession

from .extensions import db, login_manager
from .models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _serialize_user(user):
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
    }


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"message": "Authentication required."}), 401


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = User.query.filter_by(email=email).first() if email else None
    if not user:
        return jsonify({"message": "Invalid email or password."}), 401
    if not user.password_hash:
        return jsonify({"message": "This account uses SSO login only."}), 401
    if not user.check_password(password):
        return jsonify({"message": "Invalid email or password."}), 401

    login_user(user)
    return jsonify(_serialize_user(user))


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return '', 204


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify(_serialize_user(current_user))


@auth_bp.route('/config', methods=['GET'])
def auth_config():
    return jsonify({"sso_enabled": current_app.config.get('SSO_ENABLED', False)})


def _resolve_sso_user(claims):
    """Look up a local User for the given OIDC claims, auto-provisioning
    only if the user belongs to AUTHENTIK_AUTO_PROVISION_GROUP. Returns
    None if no account exists and auto-provisioning doesn't apply."""
    sub = claims.get('sub')
    email = (claims.get('email') or '').strip().lower()

    user = User.query.filter_by(authentik_sub=sub).first() if sub else None
    if user is None and email:
        user = User.query.filter_by(email=email).first()

    if user is None:
        auto_group = current_app.config.get('AUTHENTIK_AUTO_PROVISION_GROUP')
        groups = claims.get('groups') or []
        if not email or not auto_group or auto_group not in groups:
            return None
        user = User(email=email, display_name=claims.get('name') or email, authentik_sub=sub)
        db.session.add(user)

    if sub and not user.authentik_sub:
        user.authentik_sub = sub

    db.session.commit()
    return user


def init_oidc(app):
    """Register Authentik SSO routes. Only called when SSO_ENABLED is true."""
    provider_config = ProviderConfiguration(
        issuer=app.config['AUTHENTIK_ISSUER'],
        client_metadata=ClientMetadata(
            client_id=app.config['AUTHENTIK_CLIENT_ID'],
            client_secret=app.config['AUTHENTIK_CLIENT_SECRET'],
        ),
        auth_request_params={'scope': ['openid', 'email', 'profile', 'groups']},
    )
    oidc_auth = OIDCAuthentication({'default': provider_config}, app)

    @app.route('/api/auth/sso/login')
    @oidc_auth.oidc_auth('default')
    def sso_login():
        session = UserSession(flask.session)
        claims = dict(session.userinfo or session.id_token or {})
        user = _resolve_sso_user(claims)
        if user is None:
            return redirect('/?error=no_account')
        login_user(user)
        return redirect('/')

    @app.route('/api/auth/sso/logout')
    @oidc_auth.oidc_logout
    def sso_logout():
        logout_user()
        return redirect('/')

    return oidc_auth
