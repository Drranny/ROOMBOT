from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 환경변수 또는 직접 입력
POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgresql://postgres:ju041803@roombot-new.chuqo4maweif.us-east-2.rds.amazonaws.com:5432/postgres')

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SVOSentence(Base):
    __tablename__ = 'svo_sentences'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    language = Column(String(10), nullable=False)
    result = Column(Text, nullable=False)

# 테이블 생성
Base.metadata.create_all(bind=engine)

def save_svo_sentence(text: str, language: str, result: str):
    db = SessionLocal()
    svo = SVOSentence(text=text, language=language, result=result)
    db.add(svo)
    db.commit()
    db.refresh(svo)
    db.close()
    return svo
