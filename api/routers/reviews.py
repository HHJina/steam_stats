from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.models.base import get_session
from api.schemas.review import ReviewResponse, ReviewSnapshotResponse, ReviewSpikeResponse
from api.services.review import ReviewService

router = APIRouter()


@router.get("/{app_id}", response_model=list[ReviewResponse])
def get_review_list(app_id: int, limit: int = 20, offset: int = 0, session: Session = Depends(get_session)):
    return ReviewService.get_review_list(app_id, session, limit, offset)


@router.get("/{app_id}/snapshot", response_model=list[ReviewSnapshotResponse])
def get_review_snapshot(app_id: int, session: Session = Depends(get_session)):
    return ReviewService.get_review_snapshot(app_id, session)


# 리뷰급증
@router.get("/{app_id}/spikes", response_model=list[ReviewSpikeResponse])
def get_review_spikes(app_id: int, session: Session = Depends(get_session)):
    return ReviewService.get_review_spikes(app_id, session)


@router.get("/{app_id}/sentiment")
def get_sentiment(app_id: int, session: Session = Depends(get_session)):
    return ReviewService.get_sentiment(app_id, session)
