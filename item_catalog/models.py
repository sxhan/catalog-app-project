import datetime as dt

from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# from sqlalchemy import create_engine

Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=True)
    password = Column(String(250), nullable=True)
    email = Column(String(250), nullable=True)
    isoauth = Column(Boolean, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)

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
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
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
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

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
