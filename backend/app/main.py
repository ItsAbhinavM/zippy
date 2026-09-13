from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.sessions import router as session_router
from app.routes.ws import router as ws_router

app = FastAPI(title="Zippy Finance Voice Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.config import settings
print("CORS origins: ",settings.cors_origin_list)

app.include_router(session_router)
app.include_router(ws_router)

@app.get("/health")
def health():
    return {"status": "ok"}