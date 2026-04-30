# models/database.py
# Oracle DB 연결 설정

import oracledb
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

# 연결 풀 생성 (앱 시작 시 한 번만)
pool = oracledb.create_pool(
    user=DB_USER,
    password=DB_PASSWORD,
    dsn=DB_DSN,   # Oracle DB 연결 주소 
    min=2,    # 앱 시작 시 최소 연결 수
    max=10,    # 최대 연결 수
    increment=1,   # 필요 시 연결을 1개씩 추가
)
""" 미리 연결들을 만들어두고 필요할 때마다 가져다 쓰는 방식 = 풀 """


@contextmanager
def get_connection():
    """DB 연결을 풀에서 가져오고, 사용 후엔 자동 반납"""
    connection = pool.acquire()   # pool에서 연결 하나 가져오기
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        pool.release(connection)
        