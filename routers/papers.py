# | 메서드 | 엔드포인트 | 설명 | 파라미터 |
# | --- | --- | --- | --- |
# | GET | `/papers/search/keywords/{user_id}` | 유저 DB 키워드 기반 검색 | user_id |
# | GET | `/papers/search/keywords?q=AI,NLP` | 유저 입력 키워드 기반 검색 | 쿼리 파라미터로 |
# | GET | `/papers/search/category?q=cs.AI` | 카테고리 기반 검색 | category |
# | GET | `/papers/search/random` | 랜덤 카테고리 검색 | - |
# | GET | `/papers/search/published_at?from=2024-01-01&to=2024-12-31` | 날짜 기반 검색 | 쿼리 파라미터로 |
# | GET | `/papers/{arxiv_id}` | 논문 상세 조회 | arxiv_id |
# | POST | `/papers/{arxiv_id}/summarize` | 논문 요약 생성 | arxiv_id |

import random
from fastapi import APIRouter, HTTPException, Query

from services import arxiv
from services.llmSummary import summarize_paper
from models.papers import get_paper_by_id, insert_paper, update_summary
from models.users import get_user_by_id

router = APIRouter(prefix="/papers", tags=["papers"])

ARXIV_CATEGORIES = [
    # 컴퓨터과학 (Computer Science)
    "cs.AI",   # 인공지능
    "cs.AR",   # 하드웨어 아키텍처
    "cs.CC",   # 계산 복잡도
    "cs.CE",   # 전산 공학
    "cs.CG",   # 전산 기하학
    "cs.CL",   # 자연어처리
    "cs.CR",   # 암호학 및 보안
    "cs.CV",   # 컴퓨터 비전
    "cs.CY",   # 컴퓨터와 사회
    "cs.DB",   # 데이터베이스
    "cs.DC",   # 분산·병렬·클러스터 컴퓨팅
    "cs.DL",   # 디지털 라이브러리
    "cs.DM",   # 이산 수학
    "cs.DS",   # 자료구조 및 알고리즘
    "cs.ET",   # 신흥 기술
    "cs.FL",   # 형식 언어 및 오토마타
    "cs.GL",   # 일반 문헌
    "cs.GR",   # 컴퓨터 그래픽스
    "cs.GT",   # 게임 이론
    "cs.HC",   # 인간-컴퓨터 상호작용
    "cs.IR",   # 정보 검색
    "cs.IT",   # 정보 이론
    "cs.LG",   # 머신러닝
    "cs.LO",   # 논리학
    "cs.MA",   # 멀티에이전트 시스템
    "cs.MM",   # 멀티미디어
    "cs.MS",   # 수학 소프트웨어
    "cs.NA",   # 수치 해석
    "cs.NE",   # 신경망·진화 컴퓨팅
    "cs.NI",   # 네트워킹 및 인터넷
    "cs.OH",   # 기타
    "cs.OS",   # 운영체제
    "cs.PF",   # 성능
    "cs.PL",   # 프로그래밍 언어
    "cs.RO",   # 로보틱스
    "cs.SC",   # 기호 계산
    "cs.SD",   # 사운드
    "cs.SE",   # 소프트웨어 공학
    "cs.SI",   # 소셜·정보 네트워크
    "cs.SY",   # 시스템 및 제어

    # 수학 (Mathematics)
    "math.AC",  # 교환 대수학
    "math.AG",  # 대수 기하학
    "math.AP",  # 편미분 방정식
    "math.AT",  # 대수적 위상수학
    "math.CA",  # 고전 해석학
    "math.CO",  # 조합론
    "math.CT",  # 범주론
    "math.CV",  # 복소 변수
    "math.DG",  # 미분 기하학
    "math.DS",  # 동역학 시스템
    "math.FA",  # 함수 해석학
    "math.GM",  # 일반 수학
    "math.GN",  # 일반 위상수학
    "math.GR",  # 군론
    "math.GT",  # 기하학적 위상수학
    "math.HO",  # 수학사·개요
    "math.IT",  # 정보 이론
    "math.KT",  # K-이론·동형이론
    "math.LO",  # 논리학·기초
    "math.MG",  # 계량 기하학
    "math.MP",  # 수리 물리학
    "math.NA",  # 수치 해석
    "math.NT",  # 정수론
    "math.OA",  # 연산자 대수학
    "math.OC",  # 최적화·제어
    "math.PR",  # 확률론
    "math.QA",  # 양자 대수학
    "math.RA",  # 환론·대수학
    "math.RT",  # 표현론
    "math.SG",  # 심플렉틱 기하학
    "math.SP",  # 스펙트럼 이론
    "math.ST",  # 통계론

    # 통계 (Statistics)
    "stat.AP",  # 응용 통계
    "stat.CO",  # 전산 통계
    "stat.ME",  # 통계 방법론
    "stat.ML",  # 통계적 머신러닝
    "stat.OT",  # 기타 통계
    "stat.TH",  # 통계 이론

    # 물리학 (Physics)
    "astro-ph.CO",  # 우주론·은하 천체물리학
    "astro-ph.EP",  # 지구·행성 천체물리학
    "astro-ph.GA",  # 은하 천체물리학
    "astro-ph.HE",  # 고에너지 천체물리학
    "astro-ph.IM",  # 기기·방법
    "astro-ph.SR",  # 태양·항성 천체물리학
    "cond-mat.dis-nn",   # 무질서 시스템·신경망
    "cond-mat.mes-hall", # 중규모·나노스케일 물리학
    "cond-mat.mtrl-sci", # 재료 과학
    "cond-mat.other",    # 기타 응집 물질
    "cond-mat.quant-gas",# 양자 기체
    "cond-mat.soft",     # 소프트 물질
    "cond-mat.stat-mech",# 통계 역학
    "cond-mat.str-el",   # 강상관 전자계
    "cond-mat.supr-con", # 초전도
    "gr-qc",    # 일반 상대성·양자 우주론
    "hep-ex",   # 고에너지 물리학 (실험)
    "hep-lat",  # 격자 장이론
    "hep-ph",   # 고에너지 물리학 (현상론)
    "hep-th",   # 고에너지 물리학 (이론)
    "math-ph",  # 수리 물리학
    "nlin.AO",  # 적응·자기조직화
    "nlin.CD",  # 카오스·역학계
    "nlin.CG",  # 세포 자동자·격자 기체
    "nlin.PS",  # 패턴 형성·솔리톤
    "nlin.SI",  # 정확히 풀 수 있는 비선형계
    "nucl-ex",  # 핵 실험
    "nucl-th",  # 핵 이론
    "physics.acc-ph",    # 가속기 물리학
    "physics.ao-ph",     # 대기·해양 물리학
    "physics.app-ph",    # 응용 물리학
    "physics.atm-clus",  # 원자·분자 클러스터
    "physics.atom-ph",   # 원자 물리학
    "physics.bio-ph",    # 생물 물리학
    "physics.chem-ph",   # 화학 물리학
    "physics.class-ph",  # 고전 물리학
    "physics.comp-ph",   # 전산 물리학
    "physics.data-an",   # 데이터 분석
    "physics.ed-ph",     # 물리 교육
    "physics.flu-dyn",   # 유체 역학
    "physics.gen-ph",    # 일반 물리학
    "physics.geo-ph",    # 지구 물리학
    "physics.hist-ph",   # 물리학사·철학
    "physics.ins-det",   # 기기 및 검출기
    "physics.med-ph",    # 의료 물리학
    "physics.optics",    # 광학
    "physics.plasm-ph",  # 플라즈마 물리학
    "physics.pop-ph",    # 대중 물리학
    "physics.soc-ph",    # 사회 물리학
    "physics.space-ph",  # 우주 물리학
    "quant-ph",  # 양자 물리학

    # 전기공학 및 시스템 (EESS)
    "eess.AS",  # 음성·오디오 처리
    "eess.IV",  # 영상·비디오 처리
    "eess.SP",  # 신호 처리
    "eess.SY",  # 시스템·제어

    # 경제학 (Economics)
    "econ.EM",  # 계량경제학
    "econ.GN",  # 일반 경제학
    "econ.TH",  # 경제학 이론

    # 정량 생물학 (Quantitative Biology)
    "q-bio.BM",  # 분자 생물학
    "q-bio.CB",  # 세포 행동
    "q-bio.GN",  # 유전체학
    "q-bio.MN",  # 분자 네트워크
    "q-bio.NC",  # 신경·인지과학
    "q-bio.OT",  # 기타 정량 생물학
    "q-bio.PE",  # 집단·진화
    "q-bio.QM",  # 정량적 방법론
    "q-bio.SC",  # 세포하 과정
    "q-bio.TO",  # 조직·기관

    # 정량 금융 (Quantitative Finance)
    "q-fin.CP",  # 전산 금융
    "q-fin.EC",  # 경제학
    "q-fin.GN",  # 일반 금융
    "q-fin.MF",  # 수리 금융
    "q-fin.PM",  # 포트폴리오 관리
    "q-fin.PR",  # 가격 결정
    "q-fin.RM",  # 리스크 관리
    "q-fin.ST",  # 통계 금융
    "q-fin.TR",  # 트레이딩·시장 미시구조
]


@router.get("/search/keywords/{user_id}")
async def search_by_user_keywords(
    user_id: int,
    page: int = Query(1, ge=1),  # 기본값 1, 최소값 1
    size: int = Query(10, ge=1, le=50),   # 기본값 10, 최소값 1, 최대값 50 (너무 많이 가져오면 서버 부담될 수 있어서 최대 50으로 제한)
):
    """유저 DB 키워드 기반 논문 검색"""

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    if not user.get("keywords"):
        raise HTTPException(status_code=400, detail="유저의 관심 키워드가 없습니다.")
        # 지금 유저 DB에 키워드 생성 안 되어있으면 400 뜨게 해놨는데 프론트에서 400 받으면 랜덤으로 다시 돌리게 하던가 해야 함.

    keyword = user["keywords"]  # "AI, VR, cnn" 등의 형태(유저 입력)
    papers = await arxiv.search_papers(keyword=keyword, page=page, size=size)

    for paper in papers:
        insert_paper(paper)

    return {"user_id": user_id, "keyword": keyword, "page": page, "size": size, "results": papers}



@router.get("/search/keywords")
async def search_by_keywords(
    q: str = Query(..., description="검색 키워드 (예: AI,NLP)"),   # ... = 필수 파라미터, description은 API 문서에 설명으로 표시됨
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    """유저 입력 키워드 기반 논문 검색"""
    papers = await arxiv.search_papers(keyword=q, page=page, size=size)

    for paper in papers:
        insert_paper(paper)

    return {"keyword": q, "page": page, "size": size, "results": papers}


"""
TODO : 나중에는 유저 DB 키워드 검색도 q=AI,NLP 이런 식으로 여러 키워드 입력할 수 있도록 수정
"""


@router.get("/search/category")
async def search_by_category(
    category: list[str] = Query(..., description="arXiv 카테고리 (예: cs.AI)"),
    q: str = Query(None, description="추가 검색 키워드 (선택)"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    """카테고리 기반 논문 검색"""
    if q:
        papers = await arxiv.search_papers_by_category(keyword=q, category=category, page=page, size=size)
    else:
        papers = await arxiv.search_papers(keyword=f"cat:{'+'.join(category)}", page=page, size=size)

    for paper in papers:
        insert_paper(paper)

    return {"category": category, "q": q, "page": page, "size": size, "results": papers}



"""
여기까지 코드리뷰 완료 아래는 봐야 함.
"""



@router.get("/search/random")
async def search_random(
    size: int = Query(10, ge=1, le=50),
):
    """랜덤 카테고리 논문 검색"""
    category = random.choice(ARXIV_CATEGORIES)
    papers = await arxiv.search_papers(keyword=f"cat:{category}", page=1, size=size)

    for paper in papers:
        insert_paper(paper)

    return {"category": category, "results": papers}


@router.get("/search/published_at")
async def search_by_published_at(
    from_date: str = Query(..., description="시작 날짜 (예: 2024-01-01)"),
    to_date: str = Query(..., description="종료 날짜 (예: 2024-12-31)"),
    q: str = Query(None, description="추가 검색 키워드 (선택)"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    """날짜 기반 논문 검색"""
    # arXiv 날짜 형식: YYYYMMDDHHMMSS
    from_fmt = from_date.replace("-", "") + "000000"
    to_fmt = to_date.replace("-", "") + "235959"

    keyword = q if q else "all"
    date_query = f"{keyword} AND submittedDate:[{from_fmt} TO {to_fmt}]"

    papers = await arxiv.search_papers(keyword=date_query, page=page, size=size)

    for paper in papers:
        insert_paper(paper)

    return {"from_date": from_date, "to_date": to_date, "q": q, "page": page, "size": size, "results": papers}


@router.get("/{arxiv_id:path}")
async def get_paper(arxiv_id: str):
    """논문 상세 조회 — DB에 있으면 DB에서, 없으면 arXiv에서 가져옴"""
    # DB에서 먼저 조회
    paper = get_paper_by_id(arxiv_id)

    if not paper:
        # DB에 없으면 arXiv에서 가져와서 저장
        paper = await arxiv.get_paper(arxiv_id)
        if not paper:
            raise HTTPException(status_code=404, detail="논문을 찾을 수 없습니다.")
        insert_paper(paper)

    return paper


@router.post("/{arxiv_id:path}/summarize")
async def summarize(arxiv_id: str):
    """논문 한국어 요약 생성 — DB에 캐시, 이미 있으면 재사용"""
    paper = get_paper_by_id(arxiv_id)

    if not paper:
        paper = await arxiv.get_paper(arxiv_id)
        if not paper:
            raise HTTPException(status_code=404, detail="논문을 찾을 수 없습니다.")
        insert_paper(paper)

    # 이미 요약 있으면 캐시 반환
    if paper.get("summary_ko"):
        return {"arxiv_id": arxiv_id, "summary": paper["summary_ko"], "cached": True}

    # 없으면 Groq API 호출
    summary = summarize_paper(title=paper["title"], abstract=paper["abstract"])
    if not summary:
        raise HTTPException(status_code=502, detail="요약 생성에 실패했습니다.")

    # DB에 저장
    import json
    update_summary(arxiv_id=arxiv_id, summary_ko=json.dumps(summary, ensure_ascii=False))

    return {"arxiv_id": arxiv_id, "summary": summary, "cached": False}