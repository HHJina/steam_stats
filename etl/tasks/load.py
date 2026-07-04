import os

import pandas as pd
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv("/opt/airflow/steam_stats/.env")


def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def get_valid_app_ids(cursor) -> set:
    cursor.execute("SELECT app_id FROM games")
    return {row[0] for row in cursor.fetchall()}


def load_games(df: pd.DataFrame):
    conn = get_conn()
    cursor = conn.cursor()
    records = df.to_dict("records")

    if not records:
        cursor.close()
        conn.close()
        return

    columns = [
        "app_id", "name", "developer", "publisher",
        "is_free", "is_indie", "release_date", "header_image",
        "metacritic_score", "metacritic_url", "peak_in_game",
    ]

    values = [tuple(row.get(col) for col in columns) for row in records]

    try:
        # row-by-row execute() 대신 execute_values로 한 번에 배치 insert/upsert
        # (기존 방식은 수백 건을 개별 왕복으로 처리해 poll 루프 밖 처리 시간이
        # max_poll_interval_ms를 초과시키는 원인이었음)
        psycopg2.extras.execute_values(
            cursor,
            """
            INSERT INTO games (
                app_id, name, developer, publisher,
                is_free, is_indie, release_date, header_image,
                metacritic_score, metacritic_url, peak_in_game,
                collected_at
            )
            VALUES %s
            ON CONFLICT (app_id) DO UPDATE SET
                name = EXCLUDED.name,
                developer = EXCLUDED.developer,
                publisher = EXCLUDED.publisher,
                is_free = EXCLUDED.is_free,
                is_indie = EXCLUDED.is_indie,
                release_date = EXCLUDED.release_date,
                header_image = EXCLUDED.header_image,
                metacritic_score = EXCLUDED.metacritic_score,
                metacritic_url = EXCLUDED.metacritic_url,
                peak_in_game = EXCLUDED.peak_in_game,
                collected_at = NOW()
            """,
            values,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())",
        )
        conn.commit()
    except Exception as e:
        print(f"에러: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def load_genres(df: pd.DataFrame):
    conn = get_conn()
    cursor = conn.cursor()
    valid_app_ids = get_valid_app_ids(cursor)
    records = [row for row in df.to_dict("records") if row["app_id"] in valid_app_ids]

    for row in records:
        try:
            cursor.execute(
                """
                INSERT INTO genres (name)
                VALUES (%(genre_name)s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
                """,
                row,
            )
            result = cursor.fetchone()

            if not result:
                cursor.execute("SELECT id FROM genres WHERE name = %(genre_name)s", row)
                result = cursor.fetchone()

            genre_id = result[0]

            cursor.execute(
                """
                INSERT INTO game_genres (app_id, genre_id)
                VALUES (%(app_id)s, %(genre_id)s)
                ON CONFLICT DO NOTHING
                """,
                {"app_id": row["app_id"], "genre_id": genre_id},
            )
        except Exception as e:
            print(f"에러 발생 row: {row}")
            print(f"에러: {e}")
            conn.rollback()
            raise
    conn.commit()
    cursor.close()
    conn.close()


def load_prices(df: pd.DataFrame):
    conn = get_conn()
    cursor = conn.cursor()
    valid_app_ids = get_valid_app_ids(cursor)
    records = [row for row in df.to_dict("records") if row["app_id"] in valid_app_ids]

    if records:
        try:
            psycopg2.extras.execute_batch(
                cursor,
                """
                INSERT INTO price_history (app_id, price, original_price, discount_rate, collected_at)
                VALUES (%(app_id)s, %(price)s, %(original_price)s, %(discount_rate)s, NOW())
                """,
                records,
            )
            conn.commit()
        except Exception as e:
            print(f"에러: {e}")
            conn.rollback()
            raise
    cursor.close()
    conn.close()


def load_player_counts(df: pd.DataFrame):
    conn = get_conn()
    cursor = conn.cursor()
    valid_app_ids = get_valid_app_ids(cursor)
    records = [row for row in df.to_dict("records") if row["app_id"] in valid_app_ids]

    if records:
        try:
            psycopg2.extras.execute_batch(
                cursor,
                """
                INSERT INTO player_counts (app_id, player_count, collected_at)
                VALUES (%(app_id)s, %(player_count)s, NOW())
                """,
                records,
            )
            conn.commit()
        except Exception as e:
            print(f"에러: {e}")
            conn.rollback()
            raise
    cursor.close()
    conn.close()


def load_review_snapshots(df: pd.DataFrame):
    conn = get_conn()
    cursor = conn.cursor()
    valid_app_ids = get_valid_app_ids(cursor)
    records = [row for row in df.to_dict("records") if row["app_id"] in valid_app_ids]

    if records:
        try:
            psycopg2.extras.execute_batch(
                cursor,
                """
                INSERT INTO reviews_snapshot (
                    app_id, total_reviews, positive_reviews, negative_reviews,
                    positive_ratio, collected_at
                )
                VALUES (
                    %(app_id)s, %(total_reviews)s, %(positive_reviews)s,
                    %(negative_reviews)s, %(positive_ratio)s, NOW()
                )
                """,
                records,
            )
            conn.commit()
        except Exception as e:
            print(f"에러: {e}")
            conn.rollback()
            raise
    cursor.close()
    conn.close()


def load_reviews(df: pd.DataFrame):
    conn = get_conn()
    cursor = conn.cursor()
    valid_app_ids = get_valid_app_ids(cursor)

    cursor.execute("SELECT review_id FROM review_texts")
    existing_ids = {row[0] for row in cursor.fetchall()}

    records = [
        row for row in df.to_dict("records") if row["review_id"] not in existing_ids and row["app_id"] in valid_app_ids
    ]

    seen_ids = set()
    unique_records = []
    for row in records:
        if row["review_id"] not in seen_ids:
            seen_ids.add(row["review_id"])
            unique_records.append(row)
    records = unique_records

    if records:
        try:
            psycopg2.extras.execute_batch(
                cursor,
                """
                INSERT INTO review_texts (
                    review_id, app_id, review_text, voted_up,
                    playtime_hours, language, created_at, collected_at
                )
                VALUES (
                    %(review_id)s, %(app_id)s, %(review_text)s, %(voted_up)s,
                    %(playtime_hours)s, %(language)s, %(created_at)s, NOW()
                )
                """,
                records,
            )
            conn.commit()
        except Exception as e:
            print(f"에러: {e}")
            conn.rollback()
            raise
    cursor.close()
    conn.close()


def load_genre_stats(df: pd.DataFrame):
    conn = get_conn()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        try:
            cursor.execute("SELECT id FROM genres WHERE name = %s", (row["genre_name"],))
            result = cursor.fetchone()

            if not result:
                continue

            genre_id = result[0]

            cursor.execute(
                """
                INSERT INTO genre_stats (genre_id, avg_price, avg_positive_ratio, total_games, calculated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING
            """,
                (
                    genre_id,
                    row["avg_price"] or 0,
                    row["avg_positive_ratio"] or 0,
                    row["total_games"],
                ),
            )

        except Exception as e:
            print(f"에러: {e}")
            conn.rollback()
            raise

    conn.commit()
    cursor.close()
    conn.close()


def load_hidden_gems(df: pd.DataFrame):
    conn = get_conn()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        try:
            cursor.execute(
                """
                INSERT INTO hidden_gems (
                    app_id, gem_score, positive_ratio,
                    review_count, recent_positive_ratio, calculated_at
                )
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (app_id, calculated_at) DO NOTHING
            """,
                (
                    int(row["app_id"]),
                    float(row["gem_score"]),
                    float(row["positive_ratio"]),
                    int(row["review_count"]),
                    float(row["recent_positive_ratio"]),
                ),
            )
        except Exception as e:
            print(f"에러: {e}")
            conn.rollback()
            raise

    conn.commit()
    cursor.close()
    conn.close()


def load_review_analysis(df: pd.DataFrame):
    conn = get_conn()
    cursor = conn.cursor()
    records = df.to_dict("records")

    if records:
        try:
            psycopg2.extras.execute_batch(
                cursor,
                """
                INSERT INTO review_analysis (review_id, sentiment_score, calculated_at)
                VALUES (%(review_id)s, %(sentiment_score)s, NOW())
                ON CONFLICT (review_id) DO NOTHING
                """,
                records,
            )
            conn.commit()
        except Exception as e:
            print(f"에러: {e}")
            conn.rollback()
            raise
    cursor.close()
    conn.close()