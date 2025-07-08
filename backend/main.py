from fastapi import FastAPI
from api.routes import router
from api.auth_routes import router as auth_router
from api.protected_routes import router as protected_router
from config.firebase_config import initialize_firebase
from api.users import router as users_router

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
app.include_router(users_router, prefix="/api")

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
