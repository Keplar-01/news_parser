from sqlalchemy import Column, Integer, Float, VARCHAR,Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    title = Column(VARCHAR(255), nullable=False)
    url = Column(VARCHAR(255), nullable=False, unique=True)
    is_train = Column(Boolean, nullable=False, default=False)
    classes = Column(VARCHAR(255))

    def __init__(self, text, title, url):
        self.text = text
        self.title = title
        self.url = url
