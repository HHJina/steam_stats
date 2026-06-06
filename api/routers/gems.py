from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from api.models.base import get_session
from api.services.gem import GemService

router = APIRouter()


# 숨은 명작 목록
@router.get("/")
def get_hidden_gems(
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    return GemService.get_hidden_gems(session, limit, offset)


# 특정 게임 gem 정보
@router.get("/{app_id}")
def get_gem(app_id: int, session: Session = Depends(get_session)):
    gem = GemService.get_gem(app_id, session)
    if not gem:
        raise HTTPException(status_code=404, detail="숨은 명작 정보를 찾을 수 없습니다")
    return gem