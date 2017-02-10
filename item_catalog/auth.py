from __future__ import absolute_import

import logging
from urlparse import urlparse, urljoin

import requests
from flask import request
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from . import app, models


# Connect to Database and create database session
engine = create_engine(app.config["DB_STRING"])
models.Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Set up login_manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "Login"


def create_user(username="", password="", email="", isoauth=False):
    if isoauth:
        if not email:
            raise ValueError("Email is required for an oauth signup")
    else:
        if not username or not password:
            raise ValueError("username and password are required!")

    user = models.User(username=username,
                       password=password,
                       email=email,
                       isoauth=isoauth)
    db_session.add(user)
    db_session.commit()
    return user


def query_oauth_user(email):
    try:
        user = (db_session.query(models.User)
                          .filter_by(email=email, isoauth=True)
                          .one())
        return user
    except NoResultFound:
        pass
    except Exception:
        logging.error("Something went wrong querying oauth user!",
                      exc_info=True)
    return None


def form_login(username, password):
    """Authentication function for form based login. Returns the user object
    when the credentials are correct, or None otherwise.
    """
    # TODO Make this secure with password hashing

    try:
        user = db_session.query(models.User).filter(username=username,
                                                    password=password).one()
        return user
    except NoResultFound:
        logging.warning("Invalid login!", exc_info=True)
    except Exception:
        logging.error("Something went wrong while logging in!", exc_info=True)
    return None


@login_manager.user_loader
def load_user(user_id):
    """Callback function used by login_manager plugin. It should take the
    unicode ID of a user, and return the corresponding user object.
    It should return None (not raise an exception) if the ID is not valid.
    (In that case, the ID will manually be removed from the session and
    processing will continue.)
    """
    try:
        user_id = int(user_id)
        user = db_session.query(models.User).filter_by(id=int(user_id)).one()
    except NoResultFound:
        logging.error("No matching user found for user_id=%s" % user_id)
        return None
    except Exception:
        logging.error("Unhandled error in load_user", exc_info=True)
        return None

    return user


def is_safe_url(target):
    """Check to protect from url redirect attacks
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def build_facebook_session(client_token):
    # Exchange client token for a long-lived server-side token
    app_id = app.config['FB_CLIENT_SECRETS']['web']['app_id']
    app_secret = app.config['FB_CLIENT_SECRETS']['web']['app_secret']
    # Send app_secret, app_id along with access token to verify both user and
    # our server.

    url = ('https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'  # NOQA
           % (app_id, app_secret, client_token))

    # Get response. This will be a string of format
    # "access_token={TOKEN}&expires={TIME}"
    r = requests.get(url)
    if r.status_code == 200:
        # strip expire tag from access token
        token_qstring = r.content.split("&")[0]
        # The token must be stored in the session in order to properly logout,
        # let's strip out the information before the equals sign in our token
        stored_token = token_qstring.split("=")[1]
    else:
        return None

    # Use token to get user info from API
    # userinfo_url = "https://graph.facebook.com/v2.4/me"
    url = ('https://graph.facebook.com/v2.4/me?%s&fields=name,id,email'
           % token_qstring)

    # Get response. This will be a json response with (email, name, id)
    r = requests.get(url)
    if r.status_code == 200:
        user_data = r.json()
    else:
        return None

    # Get user picture
    url = ('https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200'  # NOQA
           % token_qstring)
    r = requests.get(url)
    if r.status_code == 200:
        picture_data = r.json()
    else:
        return None

    return {"user": user_data["name"],
            "email": user_data["email"],
            "facebook_id": user_data["id"],
            "access_token": stored_token,
            "picture": picture_data}
