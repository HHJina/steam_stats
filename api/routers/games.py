from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from api.models.base import get_session
from api.schemas.game import GameResponse, PlayerCountResponse, PriceHistoryResponse
from api.services.game import GameService

router = APIRouter()


# 인디게임 목록 (/{app_id} 보다 먼저 선언)
@router.get("/indie/list", response_model=list[GameResponse])
def get_indie_games(limit: int = 20, session: Session = Depends(get_session)):
    return GameService.get_indie_games(limit, session)


# 장르별 게임 목록 (/{app_id} 보다 먼저 선언)
@router.get("/genre/{genre_name}", response_model=list[GameResponse])
def get_games_by_genre(genre_name: str, limit: int = 20, session: Session = Depends(get_session)):
    return GameService.get_games_by_genre(genre_name, limit, session)


# 인기 게임 목록
@router.get("/", response_model=list[GameResponse])
def get_games(limit: int = 100, offset: int = 0, session: Session = Depends(get_session)):
    return GameService.get_games(session, limit, offset)


# 게임 상세
@router.get("/{app_id}", response_model=GameResponse)
def get_game(app_id: int, session: Session = Depends(get_session)):
    game = GameService.get_game(app_id, session)
    if not game:
        raise HTTPException(status_code=404, detail="게임을 찾을 수 없습니다")
    return game


# 가격 히스토리
@router.get("/{app_id}/prices", response_model=list[PriceHistoryResponse])
def get_price_history(app_id: int, session: Session = Depends(get_session)):
    return GameService.get_price_history(app_id, session)


# 역대 최저가
@router.get("/{app_id}/prices/lowest")
def get_lowest_price(app_id: int, session: Session = Depends(get_session)):
    return GameService.get_lowest_price(app_id, session)


# 동시접속자 히스토리
@router.get("/{app_id}/players", response_model=list[PlayerCountResponse])
def get_player_counts(app_id: int, session: Session = Depends(get_session)):
    return GameService.get_player_counts(app_id, session)
