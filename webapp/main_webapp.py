from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redis.asyncio import Redis
from sqlalchemy import func, select

from common.config import get_settings
from common.db import SessionLocal
from common.models import Job, User
from common.storage import MinioStorage

cfg = get_settings()
app = FastAPI(title="AI Bot WebApp")
app.mount("/static", StaticFiles(directory="webapp/app/static"), name="static")
templates = Jinja2Templates(directory="webapp/app/templates")
redis = Redis.from_url(cfg.redis_url, decode_responses=True)


async def get_current_user(request: Request) -> User:
    token = request.query_params.get("token") or request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="No session token")
    tg_id = await redis.get(f"session:{token}")
    if not tg_id:
        raise HTTPException(status_code=401, detail="Session expired")
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.tg_id == int(tg_id)))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user




@app.post("/auth/dev/{tg_id}")
async def auth_dev(tg_id: int) -> dict:
    """Dev login helper; replace with Telegram initData validation in production."""
    import secrets

    token = secrets.token_urlsafe(24)
    await redis.set(f"session:{token}", tg_id, ex=cfg.session_ttl_seconds)
    return {"token": token, "url": f"{cfg.webapp_base_url}/cabinet?token={token}"}
@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.get("/cabinet", response_class=HTMLResponse)
async def cabinet(request: Request, user: User = Depends(get_current_user)):
    async with SessionLocal() as session:
        jobs = list(await session.scalars(select(Job).where(Job.tg_id == user.tg_id).limit(30)))
    storage = MinioStorage()
    files = []
    for job in jobs:
        for obj in job.result_files:
            files.append({"job_id": str(job.id), "url": storage.presigned_url(obj), "status": job.status, "kind": job.kind})
    return templates.TemplateResponse(
        "cabinet.html",
        {
            "request": request,
            "user": user,
            "files": files,
            "jobs_count": len(jobs),
        },
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, user: User = Depends(get_current_user)):
    if user.tg_id not in cfg.admin_id_list:
        raise HTTPException(status_code=403, detail="Forbidden")
    async with SessionLocal() as session:
        users_count = await session.scalar(select(func.count(User.id)))
        jobs_count = await session.scalar(select(func.count(Job.id)))
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "users_count": users_count or 0, "jobs_count": jobs_count or 0},
    )
