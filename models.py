from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,scoped_session

engine = create_engine('mysql://root:admin@192.168.127.55/music_spider?charset=utf8', echo=False,pool_recycle=280)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    duration = Column(String(20))
    artist_id = Column(Integer)
    album_id = Column(Integer)
    comment_count = Column(Integer)

    def __repr__(self):
        return "<Song %r>" % self.name

class Artist(Base):
    __tablename__ = 'artist'
    id = Column(String(10),primary_key=True)
    name = Column(String(100))
    category_id = Column(String(4))
    cover = Column(String(255))

    def __repr__(self):
        return "<Artist %r>" % self.name

class Album(Base):
    __tablename__ = 'album'
    id = Column(Integer,primary_key=True)
    alb_name = Column(String(255))
    alb_desc = Column(String(255))
    alb_cover = Column(String(255))
    alb_size = Column(Integer)
    artist_id = Column(String(10))
    release_time = Column(String(10))
    release_comp = Column(String(5))

    def __repr__(self):
        return "<Album %r>" % self.alb_name

class ArtistCategory(Base):
    __tablename__ = 'artist_category'
    id = Column(String(4),primary_key=True)
    name = Column(String(50))

    def __repr__(self):
        return "<ArtistCategory %r>" % self.name

class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer,primary_key=True)
    song_id = Column(Integer)
    content = Column(String(1000))
    liked_count = Column(Integer)
    timestamp = Column(String(14))
    user_id = Column(Integer)
    nickname = Column(String(255))

    def __repr__(self):
        return "<Comments %r>" % self.content
