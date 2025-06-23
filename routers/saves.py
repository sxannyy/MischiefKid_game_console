from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
import hashlib, re

import settings, models
from db import get_db
from utils.hasher import Hasher
from supabase import create_client, Client

router = APIRouter(prefix="/saves", tags=["saves"])
supabase: Client = create_client(settings.settings.SUPABASE_URL,
                                 settings.settings.SUPABASE_KEY)

SAFE_USER = r"-_.A-Za-z0-9"

def safe_user_folder(name: str) -> str:
    """Папка = username, очищенный от странных символов"""
    return re.sub(fr"[^{SAFE_USER}]", "_", name) or "user"

@router.post("/upload")
async def upload_save(
    username: str = Form(...),
    token: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(404, "User not found")

    tok = db.query(models.Token).filter(models.Token.username == username).first()
    if not tok:
        raise HTTPException(401, "Token not found")
    if tok.created_at < datetime.utcnow() - timedelta(
            hours=settings.settings.ACCESS_TOKEN_EXPIRE_HOURS):
        db.delete(tok); db.commit()
        raise HTTPException(400, "Token expired")
    if not Hasher.verify(token, tok.token_hash):
        raise HTTPException(401, "Invalid token")

    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")

    folder  = safe_user_folder(username)
    sha1    = hashlib.sha1(file.filename.encode()).hexdigest()
    ext     = Path(file.filename).suffix or ".bin"
    obj_key = f"{folder}/{sha1}{ext}"

    try:
        supabase.storage.from_(settings.settings.SUPABASE_BUCKET).upload(obj_key, data)
        public = supabase.storage.from_(settings.settings.SUPABASE_BUCKET) \
                                 .get_public_url(obj_key)
        if not isinstance(public, str):
            public = public.get("publicURL") or public["data"]["publicURL"]
    except Exception as exc:
        raise HTTPException(500, f"Upload failed: {exc}") from exc

    sep        = "&" if "?" in public else "?"
    public_url = f"{public}{sep}orig={quote(file.filename, safe='')}"

    user.save_link = public_url
    db.delete(tok); db.commit()

    return {"detail": "File uploaded", "save_link": public_url}