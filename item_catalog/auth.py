from __future__ import absolute_import

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import app, models


# Connect to Database and create database session
engine = create_engine(app.config["DB_STRING"])
models.Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


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
