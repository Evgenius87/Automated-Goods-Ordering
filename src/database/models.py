from typing import List

from enum import Enum
import enum

from sqlalchemy import Column, Integer,Float, String, Boolean, DateTime, func, Table, Enum, BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()



dish_m2m_tag = Table(
    "dish_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("dish_id", Integer, ForeignKey("dishes.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Dish_M2M_Ingredients(Base):
    __tablename__ = "dish_m2m_ingredient"
    id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"))
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantity = Column(Float)
    dish = relationship("Dish", back_populates="dish_ingredients")
    ingredient = relationship("Ingredient", back_populates="ingredient_dishes")


class Dish_M2M_Premixes(Base):
    __tablename__ = "dish_m2m_premix"
    id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"))
    premix_id = Column(Integer, ForeignKey("premixes.id", ondelete="CASCADE"))
    quantity = Column(Float)
    dish = relationship("Dish", back_populates="dish_premixes")
    premix = relationship("Premix", back_populates="premix_dishes")


class Premix_M2M_Ingredient(Base):
    __tablename__ = 'premix_m2m_ingredient'
    id = Column(Integer, primary_key=True)
    premix_id = Column(Integer, ForeignKey('premixes.id', ondelete="CASCADE"))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id', ondelete="CASCADE"))
    quantity = Column(Float) 
    premix = relationship("Premix", back_populates="premix_ingredients")
    ingredient = relationship("Ingredient", back_populates="ingredient_premixes")


class Dish(Base):
    __tablename__ = "dishes"
    id = Column(Integer, primary_key=True)
    image_url = Column(String(255), nullable=True)
    image_public_id = Column(String(255))
    dish_name = Column(String(200), unique=True)
    description = Column(String(900))
    dish_ingredients = relationship("Dish_M2M_Ingredients", back_populates="dish")
    dish_premixes = relationship("Dish_M2M_Premixes", back_populates="dish")
    comments = relationship('Comment', back_populates="dish")
    tags = relationship("Tag", secondary=dish_m2m_tag, back_populates="dishes")
    stop_list = Column(Boolean)
    runing_out = Column(Boolean)
    need_to_sold = Column(Boolean)
    price = Column(Integer)
    created_at = Column("created_at", DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, onupdate=func.now())
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship('Category', back_populates='dishes')


class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    product_id = Column(String(200))
    amount = Column(Float)
    suma = Column(Float)
    ingredient_dishes = relationship("Dish_M2M_Ingredients", back_populates="ingredient")
    ingredient_premixes = relationship("Premix_M2M_Ingredient", back_populates="ingredient")
    stock_minimum = Column(Float, default=0.1)
    min_acceptable = Column(Float, default=0.03)
    stock_maximum = Column(Float, default=3.0)
    standart_container = Column(Float, default=1.0)
    measure = Column(String(50), default='кг')
    provider_id = Column(Integer, ForeignKey('providers.id'))
    provider = relationship('Provider', back_populates='ingredients')
    using = Column(Boolean, default=True)
    created_at = Column("created_at", DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, onupdate=func.now())


class Premix(Base):
    __tablename__ = "premixes"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True)
    premix_dishes = relationship("Dish_M2M_Premixes", back_populates="premix")
    premix_ingredients = relationship("Premix_M2M_Ingredient", back_populates="premix")
    description = Column(String(900))
    created_at = Column("created_at", DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, onupdate=func.now())


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    parent = relationship('Category', remote_side=id, back_populates='child')
    child = relationship('Category', back_populates='parent')
    dishes = relationship('Dish', back_populates='category')



class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name_tag = Column(String(25), nullable=False, unique=True)
    dishes  = relationship("Dish", secondary=dish_m2m_tag, back_populates="tags")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    comment = Column(String(955), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship("User", back_populates="comments")
    dish_id = Column(Integer, ForeignKey('dishes.id', ondelete='CASCADE'))
    dish = relationship("Dish", back_populates="comments")
    created_at = Column("created_at", DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, default=func.now(), onupdate=func.now())




class Role(enum.Enum):
    __tablename__ = 'users_roles'
    admin: str = 'admin'
    cook: str = 'cook'
    barman: str = 'barman'
    provider_bar: str = "provider_bar"
    provider_kitchen: str = "provider_kitchen"
    provider_universal: str = "provider_universal"
    user: str = 'user'

      
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name =Column(String(150), nullable=True)
    username = Column(String(150), nullable=True)
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    chat_id = Column(BIGINT, unique=True)
    phone = Column(String(20))
    email = Column(String(100))
    password = Column(String(255))
    secret_code = Column(String(255))
    created_at = Column('created_at', DateTime, default=func.now())
    refresh_token = Column(String(255))
    banned = Column(Boolean, default=False)
    role = Column('role', Enum(Role), default=Role.user)
    information = Column(String, nullable=True)
    comments = relationship('Comment', back_populates='user')
    forward_provider_message = Column(Boolean, default=False)
    provider = relationship("Provider", back_populates="user")


class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True)
    provider_name = Column(String(200), nullable=True)
    salesman_name = Column(String(200), nullable=True)
    salesman_phone = Column(BIGINT)
    salesman_email = Column(String(100))
    username = Column(String(150), nullable=True)
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    chat_id = Column(BIGINT)
    ingredients = relationship('Ingredient', back_populates='provider')
    user_id = Column(Integer, ForeignKey('users.id'))
    role = Column('role', Enum(Role), default=Role.provider_universal)
    user = relationship("User", back_populates="provider")



class Token(Base):
    __tablename__ = "token_black_list"
    access_token = Column(String(255), primary_key=True)
    created_at = Column('created_at', DateTime, default=func.now())






