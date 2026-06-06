import pandas as pd
from sqlalchemy import text


def transform_games(messages: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(messages)

    df["release_date"] = pd.to_datetime(df["release_date"], format="%d %b, %Y", errors="coerce").dt.date

    # NaT → None 변환
    df["release_date"] = df["release_date"].astype(object).where(df["release_date"].notna(), None)

    # NaN → None 변환
    df["metacritic_score"] = df["metacritic_score"].astype(object).where(df["metacritic_score"].notna(), None)
    df["metacritic_url"] = df["metacritic_url"].astype(object).where(df["metacritic_url"].notna(), None)

    return df


def transform_genres(messages: list[dict]) -> pd.DataFrame:
    rows = []
    for message in messages:
        app_id = message["app_id"]
        for genre in message["genres"]:
            rows.append({"app_id": app_id, "genre_name": genre})
    return pd.DataFrame(rows)


def transform_review_snapshots(messages: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(messages)

    df["positive_ratio"] = df["positive_reviews"] / df["total_reviews"].replace(0, 1)
    df["positive_ratio"] = df["positive_ratio"].round(4)

    return df


def transform_prices(messages: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(messages)
    df["discount_rate"] = df["discount_rate"].round(4)

    return df


def transform_reviews(messages: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(messages)
    return df


def transform_players(messages: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(messages)
    return df


# 분석
def transform_genre_stats(conn) -> pd.DataFrame:
    result = conn.execute(
        text("""
        SELECT
            g.name AS genre_name,
            AVG(ph.price) AS avg_price,
            AVG(rs.positive_ratio) AS avg_positive_ratio,
            COUNT(DISTINCT gg.app_id) AS total_games
        FROM genres g
        JOIN game_genres gg ON g.id = gg.genre_id
        LEFT JOIN (
            SELECT DISTINCT ON (app_id) app_id, price
            FROM price_history
            ORDER BY app_id, collected_at DESC
        ) ph ON gg.app_id = ph.app_id
        LEFT JOIN (
            SELECT DISTINCT ON (app_id) app_id, positive_ratio
            FROM reviews_snapshot
            ORDER BY app_id, collected_at DESC
        ) rs ON gg.app_id = rs.app_id
        GROUP BY g.name
    """)
    )

    rows = result.fetchall()
    df = pd.DataFrame(rows, columns=["genre_name", "avg_price", "avg_positive_ratio", "total_games"])
    return df


def transform_hidden_gems(conn) -> pd.DataFrame:
    result = conn.execute(
        text("""
        SELECT
            g.app_id,
            rs.positive_ratio,
            rs.total_reviews,
            COALESCE(ph.price, 0) AS price
        FROM games g
        JOIN (
            SELECT DISTINCT ON (app_id) app_id, positive_ratio, total_reviews
            FROM reviews_snapshot
            ORDER BY app_id, collected_at DESC
        ) rs ON g.app_id = rs.app_id
        LEFT JOIN (
            SELECT DISTINCT ON (app_id) app_id, price
            FROM price_history
            ORDER BY app_id, collected_at DESC
        ) ph ON g.app_id = ph.app_id
        WHERE rs.positive_ratio >= 0.7
        AND rs.total_reviews > 0
    """)
    )

    rows = result.fetchall()
    df = pd.DataFrame(rows, columns=["app_id", "positive_ratio", "review_count", "price"])

    if df.empty:
        return df

    # Decimal → float 변환
    df["positive_ratio"] = df["positive_ratio"].astype(float)
    df["price"] = df["price"].astype(float)
    df["review_count"] = df["review_count"].astype(int)

    max_reviews = df["review_count"].max() or 1
    max_price = df["price"].max() or 1

    # gem_score 계산
    df["gem_score"] = (
        df["positive_ratio"] * 0.5 + (1 - df["review_count"] / max_reviews) * 0.3 + (1 - df["price"] / max_price) * 0.2
    ).round(4)

    # 숨은 명작 조건
    df = df[(df["positive_ratio"] >= 0.9) & (df["review_count"] <= 500)]

    df["recent_positive_ratio"] = df["positive_ratio"]

    return df


def transform_review_analysis(conn) -> pd.DataFrame:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()

    result = conn.execute(
        text("""
        SELECT rt.review_id, rt.review_text
        FROM review_texts rt
        LEFT JOIN review_analysis ra ON rt.review_id = ra.review_id
        WHERE ra.review_id IS NULL
        LIMIT 1000
    """)
    )

    rows = result.fetchall()
    if not rows:
        return pd.DataFrame()

    records = []
    for row in rows:
        scores = analyzer.polarity_scores(row.review_text)
        records.append(
            {
                "review_id": row.review_id,
                "sentiment_score": round(scores["compound"], 4),
            }
        )

    return pd.DataFrame(records)
