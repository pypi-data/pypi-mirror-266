
# from ..logger import CustomFormatter

import logging
import os

import logging
from .logger import CustomFormatter

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


from sqlalchemy import create_engine,Column,Integer,String,Float, DATE, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

engine=create_engine('sqlite:///database.db')

Base= declarative_base()

class checks(Base):
    __tablename__ = "checks"

    check_number = Column(Integer, primary_key=True)
    products = Column(String)

class companies(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True)
    link = Column(String)
    title = Column(String)
    phone = Column(String)
    address = Column(String)
    district = Column(String)
    email = Column(String)
    clicked = Column(Integer, default = 0)

class price_list(Base):
    __tablename__ = "price_list"

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    price = Column(Float)

Base.metadata.create_all(engine)