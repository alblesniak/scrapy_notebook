# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Date, DateTime, Float, Boolean, Text
from scrapy.utils.project import get_project_settings

Base = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))

def create_table(engine):
    Base.metadata.create_all(engine)

class Issue(Base):
    __tablename__ = 'issue'
    id = Column(Integer, primary_key=True)
    name = Column('name', Text(), nullable=False)
    number = Column('number', Text(), nullable=False)
    cover_url = Column('cover_url', Text())
    issue_url = Column('issue_url', Text(), nullable=False, unique=True)
    article = relationship("Article", back_populates="issue")

class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer(), primary_key=True)
    section_name = Column('section_name', Text())
    title = Column('title', Text(), nullable=False)
    authors = Column('authors', Text())
    url = Column('article_url', Text(), unique=True)
    tags = Column('tags', Text())
    intro = Column('intro', Text())
    content = Column('content', Text())
    issue_id = Column('issue_id', ForeignKey('issue.id'))
    issue = relationship('Issue', back_populates='article')