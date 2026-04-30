###
# | 메서드 | 엔드포인트 | 설명 | 파라미터 |
# |--------|-----------|------|---------|
# | GET | /papers/feed | 키워드 기반 논문 피드 반환 | keyword, page |
# | GET | /papers/search | 논문 검색 | q, category |
# | GET | /papers/{arxiv_id} | 논문 상세 + AI 요약 반환 | - |
# | POST | /papers/{arxiv_id}/summarize | Claude API로 한국어 3줄 요약 생성 (캐싱) | - |


from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

from ..models import Post, Comment

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("/feed", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    """게시글 목록 조회 (최신순)"""
    return db.query(Post).order_by(Post.created_at.desc()).all()
