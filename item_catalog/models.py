import datetime as dt

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    deleted = Column(Boolean)
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
    deleted = Column(Boolean)
    created_date = Column(DateTime,
                          default=dt.datetime.utcnow())
    updated_date = Column(DateTime,
                          default=dt.datetime.utcnow(),
                          onupdate=dt.datetime.utcnow())
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id
        }

engine = create_engine('sqlite:///categoryapp.db')

Base.metadata.create_all(engine)
