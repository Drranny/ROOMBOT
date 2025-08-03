import psycopg2
import os

def get_db_connection():
    conn = psycopg2.connect(
        dbname="postgres",  # RDS 데이터베이스명
        user="postgres",    # RDS 사용자명 (기본값)
        password="ju041803",        # RDS 비밀번호
        host="roombot-new.chuqo4maweif.us-east-2.rds.amazonaws.com",
        port="5432"
    )
    return conn 