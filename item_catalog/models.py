import datetime as dt

from flask_login import UserMixin
from sqlalchemy import (Column, ForeignKey, Integer, String, Boolean, DateTime,
                        UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker

from . import app

# from sqlalchemy import create_engine

Base = declarative_base()

# Connect to Database and create database session
engine = create_engine(app.config["DB_STRING"])
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


class User(Base, UserMixin):
    """Model of a user. The UserMixin allows flask_login to use this class for
    a global authentication check mechanism.
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=True)
    password = Column(String(250), nullable=True)
    email = Column(String(250), nullable=True)
    isoauth = Column(Boolean, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)

    # this should ensure separation between regular users and email users
    # NOTE: the comma at the end is required to make it a tuple!
    __table_args__ = (UniqueConstraint('username', 'email', 'isoauth',
                                       name='_username_email_isoauth'),)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.username,
            'email': self.email,
            'isoauth': self.isoauth,
            'is_active': self.is_active,
        }

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Category(Base):
    """Model for a category object.
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    created_date = Column(DateTime,
                          default=dt.datetime.utcnow())
    updated_date = Column(DateTime,
                          default=dt.datetime.utcnow(),
                          onupdate=dt.datetime.utcnow())

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    """Model for an item object. An item must belong to a category, and is
    associated with a creator.
    """
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    created_date = Column(DateTime,
                          default=dt.datetime.utcnow())
    updated_date = Column(DateTime,
                          default=dt.datetime.utcnow(),
                          onupdate=dt.datetime.utcnow())
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, cascade="save-update, merge, delete")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, cascade="save-update, merge, delete")

    # Ensure item uniqueness at database level
    # NOTE: the comma at the end is required to make it a tuple!
    __table_args__ = (UniqueConstraint('name', 'category_id',
                                       name='_name_category'),)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'user_id': self.user_id
        }
