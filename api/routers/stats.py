from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.models.base import get_session
from api.schemas.stats import GenreStatResponse, IndieGameResponse, TopPlayerGameResponse
from api.services.stats import StatsService

router = APIRouter()


# 장르별 통계
@router.get("/genres", response_model=list[GenreStatResponse])
def get_genre_stats(session: Session = Depends(get_session)):
    return StatsService.get_genre_stats(session)


# 동시접속자 상위 게임
@router.get("/top-players", response_model=list[TopPlayerGameResponse])
def get_top_player_games(limit: int = 20, session: Session = Depends(get_session)):
    return StatsService.get_top_player_games(session, limit)


# 장르별 인디게임
@router.get("/indie/{genre_name}", response_model=list[IndieGameResponse])
def get_indie_by_genre(genre_name: str, limit: int = 20, session: Session = Depends(get_session)):
    return StatsService.get_indie_by_genre(genre_name, session, limit)
