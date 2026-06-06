import sys

sys.path.insert(0, "/opt/airflow/steam_stats")

from datetime import datetime, timedelta

from airflow.operators.python import PythonOperator

from airflow import DAG

default_args = {
    "owner": "steam",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def run_genre_stats():
    import os

    from dotenv import load_dotenv
    from sqlalchemy import create_engine

    from etl.tasks.load import load_genre_stats
    from etl.tasks.transform import transform_genre_stats

    load_dotenv("/opt/airflow/steam_stats/.env")
    engine = create_engine(os.getenv("DATABASE_URL"))

    with engine.connect() as conn:
        df = transform_genre_stats(conn)
        load_genre_stats(df)
        print(f"genre_stats 저장 완료: {len(df)}개")


def run_hidden_gems():
    import os

    from dotenv import load_dotenv
    from sqlalchemy import create_engine

    from etl.tasks.load import load_hidden_gems
    from etl.tasks.transform import transform_hidden_gems

    load_dotenv("/opt/airflow/steam_stats/.env")
    engine = create_engine(os.getenv("DATABASE_URL"))

    with engine.connect() as conn:
        df = transform_hidden_gems(conn)
        if df.empty:
            print("hidden_gems 계산할 데이터 없음")
            return
        load_hidden_gems(df)
        print(f"hidden_gems 저장 완료: {len(df)}개")


def run_review_analysis():
    import os

    from dotenv import load_dotenv
    from sqlalchemy import create_engine

    from etl.tasks.load import load_review_analysis
    from etl.tasks.transform import transform_review_analysis

    load_dotenv("/opt/airflow/steam_stats/.env")
    engine = create_engine(os.getenv("DATABASE_URL"))

    with engine.connect() as conn:
        df = transform_review_analysis(conn)
        if df.empty:
            print("분석할 리뷰 없음")
            return
        load_review_analysis(df)
        print(f"review_analysis 저장 완료: {len(df)}개")


with DAG(
    dag_id="steam_analyze_pipeline",
    default_args=default_args,
    description="Steam 데이터 분석 파이프라인",
    schedule="0 5 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["steam", "analyze"],
) as dag:
    t_genre_stats = PythonOperator(
        task_id="run_genre_stats",
        python_callable=run_genre_stats,
    )

    t_hidden_gems = PythonOperator(
        task_id="run_hidden_gems",
        python_callable=run_hidden_gems,
    )

    t_review_analysis = PythonOperator(
        task_id="run_review_analysis",
        python_callable=run_review_analysis,
    )

    t_genre_stats >> [t_hidden_gems, t_review_analysis]
