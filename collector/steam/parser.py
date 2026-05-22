from datetime import datetime

def parse_game(raw: dict, peak_in_game: int) -> dict:
    devs = raw.get("developers")
    developer = devs[0] if devs else None
    pubs = raw.get("publishers")
    publisher = pubs[0] if pubs else None
    release_date = raw.get("release_date", {}).get("date")

    genres = raw.get("genres", [])
    is_indie = any(g["description"] == "Indie" for g in genres)

    metacritic = raw.get("metacritic", {})

    return {
        "app_id": raw.get("steam_appid"),
        "name": raw.get("name"),
        "developer": developer,
        "publisher": publisher,
        "release_date": release_date,
        "header_image": raw.get("header_image"),
        "is_free": raw.get("is_free"),
        "is_indie": is_indie,
        "metacritic_score": metacritic.get("score"),
        "metacritic_url": metacritic.get("url"),
        "peak_in_game": peak_in_game,
    }


def parse_genres(raw: dict) -> list[str]:
    genres = raw.get("genres", [])
    return [g["description"] for g in genres]


def parse_price(raw: dict) -> dict:
    price_overview = raw.get("price_overview", {})

    price = price_overview.get("final", 0) / 100
    original_price = price_overview.get("initial", 0) / 100
    discount_percent = price_overview.get("discount_percent", 0)
    discount_rate = discount_percent / 100  # 50% → 0.5

    return {
        "app_id": raw.get("steam_appid"),
        "price": price,
        "original_price": original_price,
        "discount_rate": discount_rate,
    }


def parse_review_snapshot(raw: dict, app_id: int) -> dict:
    summary = raw.get("query_summary", {})

    return {
        "app_id": app_id,
        "total_reviews": summary.get("total_reviews", 0),
        "positive_reviews": summary.get("total_positive", 0),
        "negative_reviews": summary.get("total_negative", 0),
    }


def parse_reviews(raw: dict, app_id: int) -> list[dict]:
    reviews = raw.get("reviews", [])

    results = []
    for review in reviews:
        results.append(
            {
                "review_id": review.get("recommendationid"),
                "app_id": app_id,
                "review_text": review.get("review", ""),
                "voted_up": review.get("voted_up", False),
                "playtime_hours": review["author"].get("playtime_at_review", 0),
                "language": review.get("language", "koreana"),
                "created_at": datetime.fromtimestamp(review["timestamp_created"]),
            }
        )
    return results
