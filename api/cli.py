import click
from flask.cli import AppGroup

from .extensions import db
from .models import User

user_cli = AppGroup('user', help='Manage local user accounts.')


@user_cli.command('create')
@click.option('--email', required=True, help='Email address (used for login and SSO linking).')
@click.option('--name', 'display_name', default=None, help='Display name.')
@click.option('--password', default=None, help='Password for app-managed login. Prompted if omitted.')
@click.option('--sso-only', is_flag=True, default=False, help='Create an SSO-only account with no password.')
def create_user(email, display_name, password, sso_only):
    email = email.strip().lower()
    if User.query.filter_by(email=email).first():
        raise click.ClickException(f"A user with email '{email}' already exists.")

    user = User(email=email, display_name=display_name or email)

    if not sso_only:
        if not password:
            password = click.prompt('Password', hide_input=True, confirmation_prompt=True)
        user.set_password(password)

    db.session.add(user)
    db.session.commit()

    suffix = ' [SSO-only]' if sso_only else ''
    click.echo(f"Created user '{user.email}' (id={user.id}){suffix}.")


def register_cli(app):
    app.cli.add_command(user_cli)
