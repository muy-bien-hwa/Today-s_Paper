# 📄 Today-s_Paper
 
> **논문을 릴스처럼** — 습관이 되는 학술 탐색 서비스
 
매일 뉴스는 보는데 논문은 왜 못 볼까?  
형식의 문제입니다. Today-s_Paper은 최신 논문을 짧고 가볍게, 릴스처럼 위로 스와이프하며 탐색할 수 있는 학술 콘텐츠 플랫폼입니다.
 
---
 
## 🎯 프로젝트 개요
 
| 항목 | 내용 |
|------|------|
| **프로젝트명** | Today-s_Paper |
| **목표** | 논문 접근 장벽을 낮추고, 학술 탐색을 일상 습관으로 만들기 |
| **타겟** | 논문에 관심은 있지만 읽기 막막한 대학원생·연구자·학습자 |
| **플랫폼** | Web (MVP) → iOS / Android (크로스플랫폼) |
| **개발 단계** | Phase 1 — 웹앱 MVP 개발 중 |
 
---
 
## 🚀 주요 기능
 
### 🔄 릴스형 논문 피드
- 위아래 스와이프로 논문 카드 탐색
- 관심 키워드 구독 기반 개인화 추천
- 좋아요 · 저장 · 패스 인터랙션
### 🤖 AI 요약 레이어
- Claude API를 활용한 논문 3줄 핵심 요약
- "왜 이 논문이 중요한가" 맥락 설명
- 영어 원문 → 한국어 자동 번역
- 원문 링크 제공
### 🔖 키워드 구독
- 관심 주제 태그 설정 (예: AI, 기후변화, 수면)
- arXiv · ACM · DBpia · PubMed 멀티 소스 수집
- 학회 일정 알림
### 💬 커뮤니티 (Phase 2 예정)
- 논문별 댓글 스레드
- 쉬운말 토론 문화
- 스터디 클럽 / 그룹 기능
---
 
## 🛠 기술 스택
 
### Frontend
- **React + Vite** — 웹앱 UI
- 모바일 앱 전환 예정 (React Native / Flutter)
### Backend
- **FastAPI (Python)** — REST API 서버
- **Claude API** — 논문 AI 요약 · 번역  <- 클로드로 README.md 만드니까 자기 API 쓰라고 광고하네 ㅋㅋ
### Database
- **Oracle Database 26ai** — 사용자 데이터, 논문 메타데이터, 좋아요/저장 이력
### 외부 API
- **arXiv API** — 국제 논문 수집 (무료)
- **ACM Digital Library** — 컴퓨터과학 논문
- **DBpia** — 국내 학술 논문
---
 
## 📁 프로젝트 구조
 
```
paper-reel/
├── backend/              # FastAPI 백엔드
│   ├── main.py
│   ├── routers/
│   │   ├── papers.py     # 논문 수집 · 요약 API
│   │   └── users.py      # 사용자 · 좋아요 · 저장 API
│   ├── models/           # DB 모델
│   └── services/
│       ├── arxiv.py      # arXiv API 연동
│       └── claude.py     # Claude API 요약
│
├── frontend/             # React + Vite 프론트엔드
│   ├── src(**미정**)/
│   │   ├── components/
│   │   │   ├── PaperCard.jsx     # 논문 카드 UI
│   │   │   └── SwipeFeed.jsx     # 릴스형 피드
│   │   └── pages/
│   └── vite.config.js
│
└── README.md
```
 
---
 
## 🗺 개발 로드맵
 
### ✅ Phase 1 · 웹앱 MVP (현재)
- [ ] FastAPI 백엔드 세팅
- [ ] arXiv API 논문 수집 연동
- [ ] Claude API 요약 · 번역 파이프라인
- [ ] Oracle 26ai DB 스키마 설계
- [ ] React + Vite 프론트엔드 기본 피드 UI
- [ ] 논문 카드 컴포넌트 (좋아요 · 저장)
- [ ] 키워드 구독 설정 화면
### 🔜 Phase 2 · 커뮤니티 (예정)
- 댓글 스레드 기능
- DBpia · ACM 멀티소스 연동
- 학회 일정 알림
- 사용자 프로필 · 팔로우
### 🔮 Phase 3 · 모바일 앱 (예정)
- iOS / Android 크로스플랫폼 앱 출시
- 푸시 알림 기반 "3일 1논문" 챌린지
- 개인화 추천 알고리즘 고도화

---
 
## 💡 핵심 아이디어
 
> "3일 1논문 프로젝트를 하려 했으나 막막함을 느꼈다.  
> 논문을 가볍게, 습관처럼, 재미있게 읽을 수는 없을까?"
 
논문의 진입 장벽은 **내용의 어려움**이 아니라 **형식**입니다.  
DBpia 인스타그램 채널이 반응을 얻는 이유처럼, 같은 내용도 형식이 바뀌면 다가옵니다.  
Today-s_Paper은 그 형식의 혁신을 목표로 합니다.
 
---
 
## 📄 라이선스
 
MIT License
 
---