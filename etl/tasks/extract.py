import json
import os

from kafka import KafkaConsumer


class SteamConsumer:
    def __init__(self, topic: str, group_id: str = "steam-etl"):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            group_id=group_id,
            auto_offset_reset="earliest",  # 처음부터 읽기, latest 마지막만 읽기
            enable_auto_commit=False,  # 수동커밋
            max_poll_records=500,  # 한번에 처리하는 개수
        )

    def poll(self, timeout_ms: int = 5000) -> list[dict]:
        raw_messages = self.consumer.poll(timeout_ms=timeout_ms)

        messages = []
        for topic_partition, records in raw_messages.items():
            for record in records:
                messages.append(record.value)

        return messages

    def commit(self):
        self.consumer.commit()

    def close(self):
        self.consumer.close()
