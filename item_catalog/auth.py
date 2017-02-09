from __future__ import absolute_import

import logging
from urlparse import urlparse, urljoin

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
