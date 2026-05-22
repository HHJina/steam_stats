import time

from collector.kafka.producer import SteamProducer
from collector.steam.client import SteamClient
from collector.steam.parser import parse_game, parse_genres, parse_price, parse_review_snapshot, parse_reviews


class SteamCollector:
    def __init__(self):
        self.client = SteamClient()
        self.producer = SteamProducer()

    def collect_top_games(self) -> None:
        ranks = self.client.top_rank_games()
        for rank in ranks:
            app_id = rank["appid"]
            concurrent_in_game = rank["concurrent_in_game"]
            peak_in_game = rank["peak_in_game"]

            try:
                raw = self.client.steam_app_detail(app_id)

                self.producer.send_game(parse_game(raw, peak_in_game))
                self.producer.send_genres({"app_id": app_id, "genres": parse_genres(raw)})
                self.producer.send_price(parse_price(raw))
                self.producer.send_player_count(
                    {
                        "app_id": app_id,
                        "player_count": concurrent_in_game,
                    }
                )

            except ValueError as e:
                print(f"Skipping app_id {app_id}: {e}")
            except Exception as e:
                print(f"Unexpected error on app_id {app_id}: {e}")

            time.sleep(2)

        self.producer.flush()

    import time

    def collect_reviews(self):
        ranks = self.client.top_rank_games()

        for rank in ranks:
            app_id = rank["appid"]

            try:
                collected = 0
                cursor = "*"
                is_first_page = True  # 스냅샷 중복 방지용 플래그

                while collected < 200:
                    reviews = self.client.get_reviews(app_id, cursor)

                    if not reviews.get("reviews"):
                        break

                    if is_first_page:
                        self.producer.send_review_snapshot(parse_review_snapshot(reviews, app_id))
                        is_first_page = False

                    for review in parse_reviews(reviews, app_id):
                        self.producer.send_review(review)

                    collected += len(reviews["reviews"])

                    new_cursor = reviews.get("cursor")

                    if not new_cursor or new_cursor == cursor:
                        break

                    cursor = new_cursor
                    time.sleep(1)

            except Exception as e:
                print(f"Unexpected error on app_id {app_id}: {e}")

            time.sleep(2)

        self.producer.flush()
