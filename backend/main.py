from fastapi import FastAPI
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth, experience, skills, jobs, applications, documents

app = FastAPI(title="Resume App", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(experience.router, prefix="/experience", tags=["experience"])
app.include_router(skills.router, prefix="/skills", tags=["skills"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])


@app.get("/health")
async def health():
    return {"status": "ok"}
