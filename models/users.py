# models/users.py
# USERS, USER_AUTH, USER_PAPERS 테이블 정의 + 쿼리

from models.database import get_connection


""" python -c "from models.users import create_tables; create_tables()" 로 테이블 생성 """

def create_tables():
    """USERS, USER_AUTH, USER_PAPERS 테이블 생성 (없을 때만)"""
    ddls = [
        (
            "USERS",
            """
            CREATE TABLE USERS (
                user_id       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,   -- 내부용 유저 ID, 실제로는 OAuth 제공자 정보로 유저 관리
                nickname      VARCHAR(100),    -- 유저 닉네임
                email         VARCHAR(255),
                keywords      VARCHAR(1000),   -- 유저 관심 키워드 (쉼표로 구분된 문자열)
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 가입일
            )
            """
        ),   ## profile_image VARCHAR(500),           -- 프로필 이미지 URL 이건 일단 제외, 나중에 추가할 수도
        (
            "USER_AUTH",   # OAuth 유저 인증 정보 저장 테이블
            """
            CREATE TABLE USER_AUTH (
                user_id     NUMBER       REFERENCES USERS(user_id),
                provider    VARCHAR(20)  NOT NULL,    -- OAuth 제공자 (예: 'google', 'github')
                provider_id VARCHAR(100) NOT NULL,    -- OAuth 제공자에서 발급한 고유 ID (예: 구글의 sub, 깃허브의 id)
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (provider, provider_id)
            )
            """
        ),
        (
            "USER_SAVE_PAPERS",   # 유저가 저장한 논문 기록
            """
            CREATE TABLE USER_SAVE_PAPERS (
                user_id    NUMBER      REFERENCES USERS(user_id),
                arxiv_id   VARCHAR(50) REFERENCES PAPERS(arxiv_id),    -- arXiv 논문 ID (예: '2101.00001')
                created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,    -- 저장한 날짜
                PRIMARY KEY (user_id, arxiv_id)
            )
            """
        ),
        (
            "USER_LIKE_PAPERS",    # 유저가 저장한 논문 기록
            """
            CREATE TABLE USER_LIKE_PAPERS (
                user_id    NUMBER      REFERENCES USERS(user_id),
                arxiv_id   VARCHAR(50) REFERENCES PAPERS(arxiv_id),    -- arXiv 논문 ID (예: '2101.00001')
                created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,    -- 좋아요 누른 날짜
                PRIMARY KEY (user_id, arxiv_id)
            )
            """
        ),
    ]

    with get_connection() as conn:
        cursor = conn.cursor()
        for table_name, ddl in ddls:
            try:
                cursor.execute(ddl)
                print(f"{table_name} 테이블 생성 완료")
            except Exception as e:
                if "ORA-00955" in str(e):
                    print(f"{table_name} 테이블 이미 존재 — 스킵")
                else:
                    raise


def get_user_by_id(user_id: int) -> dict | None:
    """user_id로 유저 단건 조회"""
    sql = "SELECT * FROM USERS WHERE user_id = :user_id"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, {"user_id": user_id})
        row = cursor.fetchone()
        if not row:
            return None
        columns = [col[0].lower() for col in cursor.description]
        return dict(zip(columns, row))


def get_user_by_provider(provider: str, provider_id: str) -> dict | None:
    """OAuth 제공자 정보로 유저 조회"""
    sql = """
        SELECT u.* FROM USERS u
        JOIN USER_AUTH a ON u.user_id = a.user_id
        WHERE a.provider = :provider AND a.provider_id = :provider_id
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, {"provider": provider, "provider_id": provider_id})
        row = cursor.fetchone()
        if not row:
            return None
        columns = [col[0].lower() for col in cursor.description]
        return dict(zip(columns, row))


def insert_user(nickname: str, email: str | None, profile_image: str | None) -> int:
    """유저 생성 후 user_id 반환"""
    sql = """
        INSERT INTO USERS (nickname, email, profile_image)
        VALUES (:nickname, :email, :profile_image)
        RETURNING user_id INTO :user_id
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        user_id_var = cursor.var(int)
        cursor.execute(sql, {
            "nickname": nickname,
            "email": email,
            "profile_image": profile_image,
            "user_id": user_id_var,
        })
        return user_id_var.getvalue()[0]


def insert_user_auth(user_id: int, provider: str, provider_id: str):
    """OAuth 인증 정보 저장"""
    sql = """
        INSERT INTO USER_AUTH (user_id, provider, provider_id)
        VALUES (:user_id, :provider, :provider_id)
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, {
            "user_id": user_id,
            "provider": provider,
            "provider_id": provider_id,
        })


def update_user_keywords(user_id: int, keywords: str):
    """관심 키워드 업데이트"""
    sql = "UPDATE USERS SET keywords = :keywords WHERE user_id = :user_id"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, {"keywords": keywords, "user_id": user_id})


def toggle_save(user_id: int, arxiv_id: str) -> bool:
    """논문 저장 토글 — 저장 여부 반환"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM USER_SAVE_PAPERS WHERE user_id = :user_id AND arxiv_id = :arxiv_id",
            {"user_id": user_id, "arxiv_id": arxiv_id}
        )
        exists = cursor.fetchone() is not None

        if exists:
            # 이미 저장 → 삭제 (저장 취소)
            cursor.execute(
                "DELETE FROM USER_SAVE_PAPERS WHERE user_id = :user_id AND arxiv_id = :arxiv_id",
                {"user_id": user_id, "arxiv_id": arxiv_id}
            )
            conn.commit()
            return False
        else:
            # 저장 안 됨 → 추가
            cursor.execute(
                "INSERT INTO USER_SAVE_PAPERS (user_id, arxiv_id) VALUES (:user_id, :arxiv_id)",
                {"user_id": user_id, "arxiv_id": arxiv_id}
            )
            conn.commit()
            return True


def toggle_like(user_id: int, arxiv_id: str) -> bool:
    """논문 좋아요 토글 — 좋아요 여부 반환"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM USER_LIKE_PAPERS WHERE user_id = :user_id AND arxiv_id = :arxiv_id",
            {"user_id": user_id, "arxiv_id": arxiv_id}
        )
        exists = cursor.fetchone() is not None

        if exists:
            # 이미 좋아요 → 삭제 (좋아요 취소)
            cursor.execute(
                "DELETE FROM USER_LIKE_PAPERS WHERE user_id = :user_id AND arxiv_id = :arxiv_id",
                {"user_id": user_id, "arxiv_id": arxiv_id}
            )
            conn.commit() 
            return False
        else:
            # 좋아요 안 됨 → 추가
            cursor.execute(
                "INSERT INTO USER_LIKE_PAPERS (user_id, arxiv_id) VALUES (:user_id, :arxiv_id)",
                {"user_id": user_id, "arxiv_id": arxiv_id}
            )
            conn.commit()
            return True


def get_saved_papers(user_id: int) -> list[dict]:
    """저장한 논문 목록 조회"""
    sql = """
        SELECT p.* FROM PAPERS p
        JOIN USER_SAVE_PAPERS sp ON p.arxiv_id = sp.arxiv_id
        WHERE sp.user_id = :user_id
        ORDER BY sp.created_at DESC
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, {"user_id": user_id})
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]


def get_liked_papers(user_id: int) -> list[dict]:
    """좋아요한 논문 목록 조회"""
    sql = """
        SELECT p.* FROM PAPERS p
        JOIN USER_LIKE_PAPERS lp ON p.arxiv_id = lp.arxiv_id
        WHERE lp.user_id = :user_id
        ORDER BY lp.created_at DESC
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, {"user_id": user_id})
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]