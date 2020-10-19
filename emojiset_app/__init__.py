from flask import Flask
import redis
from rq import Queue, Worker
from flask_bootstrap import Bootstrap
import emoji
import rq_dashboard

# ---initialises flask app---*
app = Flask(__name__)   

# ---creates an rq dashboard for us (check website/rq url)---*
app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
bootstrap = Bootstrap(app)

# ---create a job queue and connect to the Redis server
r = redis.Redis()
q = Queue(connection=r, default_timeout=120)

# ---populate EMOJI_SET---*
EMOJI_SET = set()
def pop_emoji_set():
    for emoji_char in emoji.UNICODE_EMOJI:
        EMOJI_SET.add(emoji_char)
pop_emoji_set()


from emojiset_app import views
from emojiset_app import tasks
