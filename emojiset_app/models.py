from flask_user import UserMixin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from emojiset_app import db, secret_key
import sqlalchemy as sa
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import Fernet

# Define the User data-model.
# NB: Make sure to add flask_user UserMixin !!!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    country = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    description = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

    access_token = db.Column(EncryptedType(db.String, secret_key))
    access_token_secret = db.Column(EncryptedType(db.String, secret_key))
    consumer_key = db.Column(EncryptedType(db.Unicode, secret_key))
    consumer_secret = db.Column(EncryptedType(db.Unicode, secret_key))

    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')
    

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class SavedQuery(db.Model):
    __tablename__ = 'saved_queries'
    id = db.Column(db.Integer(), primary_key=True)
    user_email = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    saved_query = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))


class RunningTask(db.Model):
    __tablename__ = 'running_tasks'
    id = db.Column(db.Integer(), primary_key=True)
    user_email = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    task_query = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    status_url = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    cancel_url = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    started_on = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    finished_on = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))


class FinishedTask(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_email = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    task_query = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    started_on = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    finished_on = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))


class SavedResultDirectory(db.Model):
    __tablename__ = 'saved_result_directory'
    id = db.Column(db.Integer(), primary_key=True)
    directory = db.Column(db.String(255, collation='NOCASE'),nullable=False, server_default='')


class EmojisetModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.has_roles('Admin'):
            return True
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('user.login', next=request.url))
