from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import json

# 환경변수 또는 직접 입력
POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgresql://jang-yunjeong@localhost:5432/postgres')

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SVOSentence(Base):
    __tablename__ = 'svo_sentences'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    language = Column(String(10), nullable=False)
    result = Column(Text, nullable=False)

class UserData(Base):
    __tablename__ = 'user_data'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), index=True, nullable=False)
    data = Column(Text, nullable=False)  # JSON 직렬화된 데이터
    created_at = Column(DateTime, default=datetime.utcnow)

class GuestData(Base):
    __tablename__ = 'guest_data'
    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(String(128), index=True, nullable=False)
    data = Column(Text, nullable=False)  # JSON 직렬화된 데이터
    created_at = Column(DateTime, default=datetime.utcnow)


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

def save_user_data(user_id: str, data: dict):
    db = SessionLocal()
    user_data = UserData(user_id=user_id, data=json.dumps(data))
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    db.close()
    return user_data

def get_user_data(user_id: str):
    db = SessionLocal()
    user_data = db.query(UserData).filter(UserData.user_id == user_id).order_by(UserData.created_at.desc()).first()
    db.close()
    if user_data:
        return json.loads(user_data.data)
    return None

def save_guest_data(guest_id: str, data: dict):
    db = SessionLocal()
    guest_data = GuestData(guest_id=guest_id, data=json.dumps(data))
    db.add(guest_data)
    db.commit()
    db.refresh(guest_data)
    db.close()
    return guest_data


def get_guest_data(guest_id: str):
    db = SessionLocal()
    guest_data = db.query(GuestData).filter(GuestData.guest_id == guest_id).order_by(GuestData.created_at.desc()).first()
    db.close()
    if guest_data:
        return json.loads(guest_data.data)
    return None

def merge_guest_to_user_data(guest_id: str, user_id: str, merge_strategy: str = 'replace'):
    """
    게스트 데이터를 사용자 데이터로 이전(merge)합니다.
    merge_strategy: 'replace' (기존 사용자 데이터 덮어씀), 'append' (리스트 등일 때 합침) 등 확장 가능
    """
    guest_data = get_guest_data(guest_id)
    if guest_data is None:
        return None
    if merge_strategy == 'replace':
        # 기존 사용자 데이터 무시, 게스트 데이터로 저장
        return save_user_data(user_id, guest_data)
    elif merge_strategy == 'append':
        # 기존 사용자 데이터와 합침 (리스트 데이터 예시)
        user_data = get_user_data(user_id) or []
        if isinstance(user_data, list) and isinstance(guest_data, list):
            merged = user_data + guest_data
            return save_user_data(user_id, merged)
        else:
            # 타입 불일치 시 replace
            return save_user_data(user_id, guest_data)
    else:
        # 기본은 replace
        return save_user_data(user_id, guest_data)
