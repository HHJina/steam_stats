import httpx


class SteamClient:
    def __init__(self):
        self.store_url = "https://store.steampowered.com"
        self.api_url = "https://api.steampowered.com"
        self.session = httpx.Client(timeout=10)

    def steam_app_detail(self, app_id: int):
        response = self.session.get(
            f"{self.store_url}/api/appdetails",
            params={"appids": app_id, "cc": "kr"},  # 한국 가격
        ).json()

        result = response[str(app_id)]
        if not result["success"]:
            raise ValueError(f"app_id {app_id}가 존재하지 않습니다")
        return result["data"]

    def top_rank_games(self):
        response = self.session.get(f"{self.api_url}/ISteamChartsService/GetGamesByConcurrentPlayers/v1/").json()

        # appids = [game["appid"] for game in response["response"]["ranks"]]

        return response["response"]["ranks"]

    def get_reviews(self, app_id: int, cursor: str = "*"):
        response = self.session.get(
            f"{self.store_url}/appreviews/{app_id}",
            params={
                "json": 1,
                "language": "koreana",
                "num_per_page": 100,
                "filter": "recent",
                "cursor": cursor,
            },
        ).json()

        return response
