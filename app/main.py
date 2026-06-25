from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.candidate.routes import router as candidate_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(candidate_router)

@app.get("/")
def root():
    return {"message": "Startup Hire API Running"}