from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

import schemas
import models
from db import get_db
from utils.hasher import Hasher
import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/verify", response_model=schemas.SaveLinkResponse)
def verify_token(data: schemas.TokenCheck, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    token_entry = db.query(models.Token).filter(models.Token.username == data.username).first()
    if not token_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")

    expire_time = timedelta(hours=settings.settings.ACCESS_TOKEN_EXPIRE_HOURS)
    if token_entry.created_at < datetime.utcnow() - expire_time:
        db.delete(token_entry)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")

    if not Hasher.verify(data.token, token_entry.token_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    db.delete(token_entry)
    db.commit()

    return {"save_link": user.save_link or ""}