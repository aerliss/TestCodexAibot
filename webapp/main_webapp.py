from __future__ import annotations

import secrets

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redis.asyncio import Redis
from sqlalchemy import func, select

from bot.app.services.repository import user_jobs
from common.config import get_settings
from common.db import SessionLocal
from common.models import User
from common.security import WebAppSigner
from common.storage import MinioStorage

cfg = get_settings()
app = FastAPI(title="AI Bot WebApp")
app.mount("/static", StaticFiles(directory="webapp/app/static"), name="static")
templates = Jinja2Templates(directory="webapp/app/templates")
redis = Redis.from_url(cfg.redis_url, decode_responses=True)
signer = WebAppSigner()


async def resolve_tg_id(request: Request) -> int:
    token = request.query_params.get("token") or request.cookies.get("session")
    if token:
        tg_id = await redis.get(f"session:{token}")
        if tg_id:
            return int(tg_id)

    auth = request.query_params.get("auth")
    if auth:
        tg_id = signer.parse(auth)
        if tg_id is not None:
            session_token = secrets.token_urlsafe(24)
            await redis.set(f"session:{session_token}", tg_id, ex=cfg.session_ttl_seconds)
            return tg_id

    raise HTTPException(status_code=401, detail="Требуется авторизация")


async def current_user(request: Request) -> User:
    tg_id = await resolve_tg_id(request)
    async with SessionLocal() as s:
        user = await s.scalar(select(User).where(User.tg_id == tg_id))
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@app.post("/auth/dev/{tg_id}")
async def auth_dev(tg_id: int) -> dict:
    token = secrets.token_urlsafe(24)
    await redis.set(f"session:{token}", tg_id, ex=cfg.session_ttl_seconds)
    return {"token": token, "url": f"{cfg.webapp_base_url}/cabinet?token={token}"}


@app.get("/cabinet", response_class=HTMLResponse)
async def cabinet(request: Request, user: User = Depends(current_user)):
    storage = MinioStorage()
    cards = []
    for job in await user_jobs(user.tg_id, 30):
        for path in job.result_files:
            cards.append({"job": str(job.id), "kind": job.kind, "status": job.status, "url": storage.url(path)})
    return templates.TemplateResponse("cabinet.html", {"request": request, "user": user, "cards": cards})


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, user: User = Depends(current_user)):
    if user.tg_id not in cfg.admin_id_list:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    async with SessionLocal() as s:
        users = await s.scalar(select(func.count(User.id)))
    return templates.TemplateResponse("admin.html", {"request": request, "users": users or 0})
