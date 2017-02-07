import datetime as dt

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=True)
    password = Column(String(250), nullable=True)
    email = Column(String(250), nullable=True)
    isoauth = Column(Boolean, nullable=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.username,
            'email': self.email,
            'isoauth': self.isoauth
        }


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
#
# engine = create_engine('sqlite:///categoryapp.db')
#
# Base.metadata.create_all(engine)
