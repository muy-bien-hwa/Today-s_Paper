# models/paper.py
# PAPERS 테이블 정의 + 쿼리

from models.database import get_connection



""" python -c "from models.papers import create_table; create_table()" 로 테이블 생성 """

def create_table():
    """PAPERS 테이블 생성 (없을 때만)"""
    ddl = """
        CREATE TABLE PAPERS (
            arxiv_id     VARCHAR(50)   PRIMARY KEY,    -- arXiv 논문 ID (예: '2101.00001')
            title        VARCHAR(1000) NOT NULL,
            abstract     CLOB,      -- CLOB = VARCHAR 보다 큰 텍스트 저장용
            summary_ko   CLOB,   
            authors      VARCHAR(2000),
            category     VARCHAR(100),    -- 논문 카테고리 (예: cs.AI, stat.ML)
            published_at DATE
        )
    """
    
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(ddl)
            print("PAPERS 테이블 생성 완료")
        except Exception as e:
            if "ORA-00955" in str(e):  # 이미 테이블 존재
                print("PAPERS 테이블 이미 존재 — 스킵")
            else:
                raise



def insert_paper(paper: dict):
    """논문 1개 저장 (이미 있으면 스킵)"""
    sql = """
        INSERT INTO PAPERS (arxiv_id, title, abstract, authors, category, published_at)
        VALUES (:arxiv_id, :title, :abstract, :authors, :category, 
                TO_DATE(:published_at, 'YYYY-MM-DD'))
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, paper)
        except Exception as e:
            if "ORA-00001" in str(e):  # PK 중복 (이미 존재)
                pass
            else:
                raise


def get_paper_by_id(arxiv_id: str) -> dict | None:
    """arxiv_id로 논문 단건 조회"""
    sql = "SELECT * FROM PAPERS WHERE arxiv_id = :arxiv_id"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, {"arxiv_id": arxiv_id})
        row = cursor.fetchone()
        if not row:
            return None
        columns = [col[0].lower() for col in cursor.description]
        return dict(zip(columns, row))


def get_papers_by_keyword(keyword: str, page: int = 1, size: int = 10) -> list[dict]:
    """키워드로 논문 목록 조회 (캐시에서)"""
    offset = (page - 1) * size
    sql = """
        SELECT * FROM PAPERS
        WHERE LOWER(title) LIKE :keyword
           OR LOWER(abstract) LIKE :keyword
        ORDER BY published_at DESC
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, {
            "keyword": f"%{keyword.lower()}%",
            "offset": offset,
            "size": size,
        })
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]


def update_summary(arxiv_id: str, summary_ko: str):
    """AI 요약 결과 저장"""
    sql = """
        UPDATE PAPERS SET summary_ko = :summary_ko
        WHERE arxiv_id = :arxiv_id
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, {"arxiv_id": arxiv_id, "summary_ko": summary_ko})