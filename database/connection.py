from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = 'postgresql://root:123456@postgres:5432/news_db'

engine = create_engine(db_url, echo=False)

Session = sessionmaker(bind=engine)
