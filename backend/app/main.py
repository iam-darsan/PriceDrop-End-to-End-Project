from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.routes import auth, products, alerts, history
from app.database import Base, engine
import secrets

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Price Drop Notification API",
    description="Track product prices and get notified when prices drop",
    version="1.0.0"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
    same_site="none",
    https_only=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(alerts.router)
app.include_router(alerts.router_alerts)
app.include_router(history.router)

@app.get("/")
async def root():
    return {"message": "Price Drop Notification API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
