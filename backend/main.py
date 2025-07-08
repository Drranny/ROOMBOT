from fastapi import FastAPI
from backend.api.routes import router
from backend.api.auth_routes import router as auth_router
from backend.api.protected_routes import router as protected_router
from backend.config.firebase_config import initialize_firebase

# Firebase 초기화
initialize_firebase()

app = FastAPI(
    title="ROOMBOT API",
    description="Firebase Auth가 연동된 AI 환각 탐지 API",
    version="1.0.0"
)

# 라우터 등록
app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(protected_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "ROOMBOT API with Firebase Auth",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "firebase": "initialized"}
