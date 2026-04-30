# main.py
# 백엔드 FastAPI 서버

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import papers

app = FastAPI(title="Today's Paper API")

app.include_router(papers.router)

app.add_middleware(   # CORS 설정
    CORSMiddleware,
    allow_origins=["*"],  # 개발할 때는 모든 도메인 허용, 배포 시에는 프론트엔드 도메인으로 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def running_check():
    return {"status": "ok", "message": "Backend server is running"}
