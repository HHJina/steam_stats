import sys

sys.path.insert(0, "/opt/airflow/steam_stats")

from datetime import datetime, timedelta

from airflow.operators.python import PythonOperator

from airflow import DAG
from collector.steam.collector import SteamCollector
from etl.tasks.extract import SteamConsumer
from etl.tasks.load import (
    load_games,
    load_genres,
    load_player_counts,
    load_prices,
    load_review_snapshots,
    load_reviews,
)
from etl.tasks.transform import (
    transform_games,
    transform_genres,
    transform_players,
    transform_prices,
    transform_review_snapshots,
    transform_reviews,
)

default_args = {
    "owner": "steam",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def collect_from_steam():
    collector = SteamCollector()
    collector.collect_top_games()
    collector.collect_reviews()


def process_topic(topic: str, transform_fn, load_fn):
    consumer = SteamConsumer(topic, group_id="steam-etl-v2")

    all_messages = []
    while True:
        messages = consumer.poll(timeout_ms=30000)
        if not messages:
            break
        all_messages.extend(messages)
        print(f"{topic} 누적: {len(all_messages)}개")

    if not all_messages:
        print(f"{topic} 메시지 없음")
        consumer.close()
        return

    df = transform_fn(all_messages)
    load_fn(df)
    consumer.commit()
    consumer.close()
    print(f"{topic} 처리 완료: {len(all_messages)}개")


def process_games():
    process_topic("steam-games", transform_games, load_games)


def process_genres():
    process_topic("steam-genres", transform_genres, load_genres)


def process_prices():
    process_topic("steam-prices", transform_prices, load_prices)


def process_players():
    process_topic("steam-players", transform_players, load_player_counts)


def process_review_snapshots():
    process_topic("steam-review-snapshots", transform_review_snapshots, load_review_snapshots)


def process_reviews():
    process_topic("steam-reviews", transform_reviews, load_reviews)


with DAG(
    dag_id="steam_collect_pipeline",
    default_args=default_args,
    description="Steam 데이터 수집 파이프라인",
    schedule="0 3 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["steam", "collect"],
) as dag:
    t_collect = PythonOperator(
        task_id="collect_from_steam",
        python_callable=collect_from_steam,
    )

    t_games = PythonOperator(
        task_id="process_games",
        python_callable=process_games,
    )

    t_genres = PythonOperator(
        task_id="process_genres",
        python_callable=process_genres,
    )

    t_prices = PythonOperator(
        task_id="process_prices",
        python_callable=process_prices,
    )

    t_players = PythonOperator(
        task_id="process_players",
        python_callable=process_players,
    )

    t_snapshots = PythonOperator(
        task_id="process_review_snapshots",
        python_callable=process_review_snapshots,
    )

    t_reviews = PythonOperator(
        task_id="process_reviews",
        python_callable=process_reviews,
    )

    # 수집 먼저 → 그 다음 games → 나머지 병렬
    t_collect >> t_games
    t_games >> [t_genres, t_prices, t_players, t_snapshots, t_reviews]
