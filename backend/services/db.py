from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# RDS PostgreSQL 설정
POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgresql://postgres:ju041803@roombot-new.chuqo4maweif.us-east-2.rds.amazonaws.com:5432/postgres')

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class KeywordSentence(Base):
    __tablename__ = 'keyword_sentences'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    language = Column(String(10), nullable=False)
    result = Column(Text, nullable=False)
    method = Column(String(20), nullable=False, default='simple_windows')

# 테이블 생성
Base.metadata.create_all(bind=engine)

def save_keyword_sentence(text: str, language: str, result: str, method: str = 'simple_windows'):
    db = SessionLocal()
    keyword = KeywordSentence(text=text, language=language, result=result, method=method)
    db.add(keyword)
    db.commit()
    db.refresh(keyword)
    db.close()
    return keyword
