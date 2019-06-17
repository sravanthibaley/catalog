import sys

import os

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship, backref

from sqlalchemy import create_engine

Base = declarative_base()

# class to store owner information


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True)
    admin_name = Column(String(250), nullable=False)
    admin_email = Column(String(250), nullable=False)
    admin_picture = Column(String(250))


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    admin_id = Column(Integer, ForeignKey("admin.id"))
    admin = relationship(Admin)

    @property
    def serialize(self):
        """Return object data in  easily seriazible format"""
        return {
           "name": self.name,
           "id": self.id
           }
# class to store projector database


class Product_Details(Base):
    __tablename__ = "Product_details"
    id = Column(Integer, primary_key=True)
    brandname = Column(String(250), nullable=False)
    material = Column(String(250), nullable=False)
    picture = Column(String(450), nullable=False)
    color = Column(String(250))
    price = Column(String(250))
    description = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship(Category)
    adminid = Column(Integer, ForeignKey("admin.id"))
    admin = relationship(Admin)
    # We added this serialize function to be
    # able to send JSON objects in a serializable format

    @property
    def serialize(self):
        return {
              "id": self.id,
              "brandname": self.brandname,
              "material": self.material,
              "picture": self.picture,
              "color": self.color,
              "price": self.price,
              "description": self.description,
              "category_id": self.category_id
             }


engine = create_engine("sqlite:///handbags.db")
Base.metadata.create_all(engine)
