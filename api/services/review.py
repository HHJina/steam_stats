from sqlalchemy import desc, text
from sqlmodel import Session, select

from api.models.game import ReviewSnapshot, ReviewText

SPIKE_THRESHOLD = 100


class ReviewService:
    @staticmethod
    def get_review_list(app_id: int, session: Session, limit: int = 20, offset: int = 0):
        return session.exec(
            select(ReviewText)
            .where(ReviewText.app_id == app_id)
            .order_by(desc(ReviewText.created_at))  # type: ignore[arg-type]
            .limit(limit)
            .offset(offset)
        ).all()

    @staticmethod
    def get_review_snapshot(app_id: int, session: Session, limit: int = 20, offset: int = 0):
        return session.exec(
            select(ReviewSnapshot)
            .where(ReviewSnapshot.app_id == app_id)
            .order_by(desc(ReviewSnapshot.collected_at))  # type: ignore[arg-type]
            .limit(limit)
            .offset(offset)
        ).all()

    @staticmethod
    def get_review_spikes(app_id: int, session: Session):
        result = session.execute(
            text("""
                SELECT
                    collected_at,
                    total_reviews,
                    positive_reviews,
                    negative_reviews,
                    total_reviews - LAG(total_reviews)
                        OVER (ORDER BY collected_at) AS review_delta,
                    positive_reviews - LAG(positive_reviews)
                        OVER (ORDER BY collected_at) AS positive_delta,
                    negative_reviews - LAG(negative_reviews)
                        OVER (ORDER BY collected_at) AS negative_delta
                FROM reviews_snapshot
                WHERE app_id = :app_id
                ORDER BY collected_at DESC
            """),
            {"app_id": app_id},
        )

        rows = result.fetchall()

        return [
            {
                "collected_at": row.collected_at,
                "total_reviews": row.total_reviews,
                "review_delta": max(row.review_delta or 0, 0),
                "is_positive_spike": (row.positive_delta or 0) > SPIKE_THRESHOLD,
                "is_negative_spike": (row.negative_delta or 0) > SPIKE_THRESHOLD,
            }
            for row in rows
        ]

    @staticmethod
    def get_sentiment(app_id: int, session: Session):
        result = session.execute(
            text("""
              SELECT
                  AVG(ra.sentiment_score) AS avg_sentiment,
                  COUNT(CASE WHEN ra.sentiment_score > 0.2 THEN 1 END) AS positive_count,
                  COUNT(CASE WHEN ra.sentiment_score < -0.2 THEN 1 END) AS negative_count,
                  COUNT(CASE WHEN ra.sentiment_score BETWEEN -0.2 AND 0.2 THEN 1 END) AS neutral_count
              FROM review_analysis ra
                       JOIN review_texts rt ON ra.review_id = rt.review_id
              WHERE rt.app_id = :app_id
              """),
            {"app_id": app_id},
        ).fetchone()

        if not result:
            return {
                "avg_sentiment": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
            }

        return {
            "avg_sentiment": float(result.avg_sentiment or 0),
            "positive_count": result.positive_count,
            "negative_count": result.negative_count,
            "neutral_count": result.neutral_count,
        }
