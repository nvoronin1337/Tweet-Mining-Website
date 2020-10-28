from flask import Flask
from flask_bootstrap import Bootstrap
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_admin import Admin

import emoji
import redis
from rq import Queue, Worker
import rq_dashboard
import datetime

import twitter_credentials

class ConfigClass(object):
    DEBUG=True
    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///emojiset.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'testemojiset@gmail.com'
    MAIL_PASSWORD = 'Em0jiset!'
    MAIL_DEFAULT_SENDER = 'testemojiset@gmail.com'

    # Flask-User settings
    USER_APP_NAME = "Emojiset Mining Research"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True        # Enable email authentication
    USER_ENABLE_USERNAME = False    # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@emojiset.com"

# ---populate EMOJI_SET---*
EMOJI_SET = set()
def pop_emoji_set():
    for emoji_char in emoji.UNICODE_EMOJI:
        EMOJI_SET.add(emoji_char)
pop_emoji_set()

# ---initialises flask app---*
app = Flask(__name__)   
app.config.from_object(__name__+'.ConfigClass')

# ---creates an rq dashboard for us (check website/rq url)---*
app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
bootstrap = Bootstrap(app)

# Initialize Flask-BabelEx
babel = Babel(app)
mail = Mail(app)

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)
from emojiset_app.models import User, Role, EmojisetModelView
from emojiset_app.forms import CustomUserManager

# Setup Flask-User
user_manager = CustomUserManager(app, db, User)

# Create all database tables
db.create_all()

# Create 'admin@example.com' user with 'Admin' and 'Agent' roles
if not User.query.filter(User.email == 'admin@emojiset.com').first():
    user = User(
        email='admin@emojiset.com',
        email_confirmed_at=datetime.datetime.utcnow(),
        password=user_manager.hash_password('emojiset_2020'),
        consumer_key=twitter_credentials.CONSUMER_KEY,
        consumer_secret=twitter_credentials.CONSUMER_SECRET,
        access_token = twitter_credentials.ACCESS_TOKEN,
        access_token_secret = twitter_credentials.ACCESS_TOKEN_SECRET
    )
    user.roles.append(Role(name='Admin'))
    user.roles.append(Role(name='Agent'))
    db.session.add(user)
    db.session.commit()

# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(EmojisetModelView(User, db.session))

# ---create a job queue and connect to the Redis server
r = redis.Redis()
# ---short_task_q is used for streaming small datasets from twitter (tasks timeout after 16 minutes)---*
small_task_q = Queue('small', connection=r)
# ---long_task_q is used for streaming large datasets from twitter (tasks have no timeout)
long_task_q = Queue('long', connection=r)

from emojiset_app import views
from emojiset_app import tasks
