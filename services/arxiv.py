# services/arxiv.py
# arXiv API 호출 및 논문 데이터 파싱

import httpx   
# 왜 httpx? -> FastAPI 공식 문서에서 권장하는 HTTP 클라이언트 라이브러리라서. requests보다 async 지원이 더 잘 되어 있다고 함.
# async란? -> 비동기 프로그래밍을 가능하게 해주는 기능으로, I/O 작업(예: API 호출)을 기다리는 동안 다른 작업을 할 수 있게 해줌.
# API 호출은 시간이 걸리는 작업이므로, async를 사용하면 유리하다고 함.
import xml.etree.ElementTree as ET  
# arXiv API는 XML 형식으로 응답을 주므로, XML 파싱을 위해 사용


ARXIV_API_URL = "http://export.arxiv.org/api/query"   # arXiv API 엔드포인트 URL
ARXIV_NS = "http://www.w3.org/2005/Atom"   # arXiv API의 XML 네임스페이스 (Atom 표준 사용)
# 어떻게 작동하냐면 -> arXiv API에서 반환하는 XML 문서는 Atom 형식을 따르는데, 이때 각 요소들은 "http://www.w3.org/2005/Atom" 네임스페이스에 속함.
# 좀 더 쉽게 설명하면 -> XML 문서에서 요소들을 구분하기 위해 네임스페이스라는 개념을 사용하는데, arXiv API는 Atom 표준을 따르므로 모든 요소들이 이 네임스페이스에 속하게 됨.
# 네임스페이스란 -> XML 문서에서 요소 이름이 충돌하는 것을 방지하기 위해 사용되는 고유한 식별자. 예를 들어, 다른 API에서도 "entry"라는 요소가 있을 수 있는데, 네임스페이스를 사용하면 arXiv의 "entry"와 다른 API의 "entry"를 구분할 수 있음.

"""
ARXIV API 예시 응답 (XML):

<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>   # entry 하나는 논문 하나를 나타냄.
        <title>Attention Is All You Need</title>
        <author>
            <name>Ashish Vaswani</name>
        </author>
        <category term="cs.AI" scheme="..."/>
        ...
    </entry>
</feed>

파이썬이 이 XML을 파싱하면 아래와 같이 네임스페이스가 포함된 태그로 접근해야 함:

<title>  →  {http://www.w3.org/2005/Atom}title
<entry>  →  {http://www.w3.org/2005/Atom}entry
<author> →  {http://www.w3.org/2005/Atom}author

아래 코드 보면 f"{{{ARXIV_NS}}}entry" 이런 식으로 접근하는 데, 이는 f-string에서 중괄호를 문자 그대로 쓰기 위해서 {{}}로 감싸는 것임. 그래서 실제로는 {http://www.w3.org/2005/Atom}entry가 됨.

category의 경우 속성으로 값을 가지기 때문에 .get("term") 이런 식으로 접근해야 함. 
"""



def _parse_entries(xml_text: str) -> list[dict]:
    """arXiv XML 응답을 논문 dict 리스트로 파싱"""
    root = ET.fromstring(xml_text)
    papers = []

    for entry in root.findall(f"{{{ARXIV_NS}}}entry"):   # 논문 하나하나 (= entry 요소) 반복
        raw_id = entry.findtext(f"{{{ARXIV_NS}}}id", "")   
        arxiv_id = raw_id.split("/abs/")[-1]  # URL에서 ID만 추출
        # https://arxiv.org/abs/2101.00001 이런 형식이라 split 하고 제일 뒤에 있는 거 추출 -> 2101.00001

        authors = []
        for author in entry.findall(f"{{{ARXIV_NS}}}author"):   # 저자 여러 명일 수 있으니까 반복
            name = author.findtext(f"{{{ARXIV_NS}}}name", "").strip()   
            if name:   # 이름 비어있는 경우 false
                authors.append(name)

        # 카테고리들
        categories = []
        for category_el in entry.findall(f"{{{ARXIV_NS}}}category"):
            term = category_el.get("term")
            if term:   # 빈 문자열이면 false
                categories.append(term)
        category = ", ".join(categories)

        # 날짜 (YYYY-MM-DD 형식으로 자름)
        published_raw = entry.findtext(f"{{{ARXIV_NS}}}published", "")
        published_at = published_raw[:10] if published_raw else ""   # "2024-01-15T00:00:00Z" 이런 형식이라 앞 10글자만 자르면 "2024-01-15" 됨

        papers.append({
            "arxiv_id":    arxiv_id,
            "title":       entry.findtext(f"{{{ARXIV_NS}}}title", "").strip().replace("\n", " "),
            "abstract":    entry.findtext(f"{{{ARXIV_NS}}}summary", "").strip().replace("\n", " "),
            "authors":     ", ".join(authors),   # list를 문자열로 합치는 건데 줄여서 쓰면 이렇게
            "category":    category,
            "published_at": published_at,
            "url":         raw_id,
        })

    return papers


async def search_papers(keyword: str, page: int = 1, size: int = 10) -> list[dict]:    # page는 페이지 번호, size는 페이지당 논문 수
    """키워드(1개)로 arXiv 논문 검색"""
    start = (page - 1) * size   # 0부터 시작, page 1이면 start 0, page 2면 start 10, page 3면 start 20 이런 식으로 계산

    async with httpx.AsyncClient() as client:
        response = await client.get(ARXIV_API_URL, params={
            "search_query": f"all:{keyword}",   # all: 키워드가 제목, 초록, 저자 이름 등 어디에 있든 검색
            "start":        start,
            "max_results":  size,
            "sortBy":       "submittedDate",
            "sortOrder":    "descending",
        })
        response.raise_for_status()   # HTTP 요청이 실패하면 예외 발생 (예: 404, 500 등)

    return _parse_entries(response.text)


"""
TODO : 나중에는 여러 카테고리 검색도 지원하도록 수정
TODO : all, ti(제목만), abs(초록만), au(저자만), co(논문 ID만), jr(저널만), cat(카테고리만) 이런 식으로 검색 범위 선택할 수 있도록 수정
"""


async def search_papers_by_category(keyword: str, categories: list[str], page: int = 1, size: int = 10) -> list[dict]:
    """키워드 + 카테고리로 arXiv 논문 검색"""
    start = (page - 1) * size
    cat_query = " OR ".join(f"cat:{c}" for c in categories)
    search_query = f"all:{keyword} AND ({cat_query})" if keyword else cat_query

    async with httpx.AsyncClient() as client:
        response = await client.get(ARXIV_API_URL, params={
            "search_query": search_query,
            "start":        start,
            "max_results":  size,
            "sortBy":       "relevance",
        })
        response.raise_for_status()

    return _parse_entries(response.text)


"""
TODO : 나중에는 여러 카테고리 검색도 지원하도록 수정 (수정 완)
"""


async def get_paper(arxiv_id: str) -> dict | None:
    """arxiv_id로 논문 조회"""
    async with httpx.AsyncClient() as client:
        response = await client.get(ARXIV_API_URL, params={
            "id_list": arxiv_id,
        })
        response.raise_for_status()

    papers = _parse_entries(response.text)
    return papers[0] if papers else None