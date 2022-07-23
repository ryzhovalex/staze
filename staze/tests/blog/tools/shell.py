from flask import url_for
from werkzeug.security import check_password_hash as from_hash
from werkzeug.security import generate_password_hash as to_hash
from staze import Staze, Db

from blog.app.user.user import User
from blog.app.post.post import Post


def import_std():
    """Import standard instances for testing."""
    staze = Staze.instance()
    db = Db.instance()
    # Create test request context for the app
    ctx = staze.test_request_context()
    return {
        "staze": staze, "db": db, "ctx": ctx, "url_for": url_for,
        "to_hash": to_hash, "from_hash": from_hash
    }


def import_main():
    return {'User': User, 'Post': Post}
