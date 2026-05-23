import pandas as pd


def transform_games(messages: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(messages)

    df["release_date"] = pd.to_datetime(
        df["release_date"], format="%d %b, %Y", errors="coerce"
    ).dt.date

    # NaT → None 변환
    df["release_date"] = df["release_date"].astype(object).where(
        df["release_date"].notna(), None
    )

    # NaN → None 변환
    df["metacritic_score"] = df["metacritic_score"].astype(object).where(
        df["metacritic_score"].notna(), None
    )
    df["metacritic_url"] = df["metacritic_url"].astype(object).where(
        df["metacritic_url"].notna(), None
    )

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
def transform_hidden_gems(session) -> pd.DataFrame:
    pass
    # DB에서 reviews_snapshot 읽어서
    # gem_score 계산
    # positive_ratio 높고 review_count 적은 게임


def transform_genre_stats(session) -> pd.DataFrame:
    pass
    # DB에서 games + game_genres 읽어서
    # 장르별 평균 가격/평점 집계


def transform_review_analysis(reviews: list[dict]) -> pd.DataFrame:
    pass
    # 리뷰 텍스트 NLP 분석
    # VADER로 sentiment_score 계산
