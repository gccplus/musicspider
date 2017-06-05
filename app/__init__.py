from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,scoped_session

engine = create_engine('mysql://root:admin@127.0.0.1/music_spider?charset=utf8', echo=False,pool_recycle=280)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

baseurl = 'http://music.163.com'