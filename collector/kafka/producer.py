from kafka import KafkaProducer
import json


def on_send_error(excp):
    print(f"Failed to send message to Kafka: {excp}")


class SteamProducer:
    def __init__(self, test_mode: bool = False):
        self.prefix = "test-" if test_mode else ""
        self.producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )

    def _key(self, app_id: int) -> str:
        return str(app_id)

    def send_game(self, data: dict):
        self.producer.send(
            f"{self.prefix}steam-games",
            key=self._key(data["app_id"]),
            value=data
        ).add_errback(on_send_error)

    def send_genres(self, data: dict):
        self.producer.send(
            f"{self.prefix}steam-genres",
            key=self._key(data["app_id"]),
            value=data
        ).add_errback(on_send_error)

    def send_price(self, data: dict):
        self.producer.send(
            f"{self.prefix}steam-prices",
            key=self._key(data["app_id"]),
            value=data
        ).add_errback(on_send_error)

    def send_player_count(self, data: dict):
        self.producer.send(
            f"{self.prefix}steam-players",
            key=self._key(data["app_id"]),
            value=data
        ).add_errback(on_send_error)

    def send_review_snapshot(self, data: dict):
        self.producer.send(
            f"{self.prefix}steam-review-snapshots",
            key=self._key(data["app_id"]),
            value=data
        ).add_errback(on_send_error)

    def send_review(self, data: dict):
        self.producer.send(
            f"{self.prefix}steam-reviews",
            key=self._key(data["app_id"]),
            value=data
        ).add_errback(on_send_error)

    def flush(self):
        self.producer.flush()