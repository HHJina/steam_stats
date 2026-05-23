from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "steam",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def run_hidden_gems():
    pass  # 나중에 구현

def run_genre_stats():
    pass  # 나중에 구현

def run_review_analysis():
    pass  # 나중에 구현

with DAG(
    dag_id="steam_analyze_pipeline",
    default_args=default_args,
    description="Steam 데이터 분석 파이프라인",
    schedule="0 5 * * *",   # 매일 새벽 5시 (수집 후)
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["steam", "analyze"],
) as dag:

    t_hidden_gems = PythonOperator(
        task_id="run_hidden_gems",
        python_callable=run_hidden_gems,
    )

    t_genre_stats = PythonOperator(
        task_id="run_genre_stats",
        python_callable=run_genre_stats,
    )

    t_review_analysis = PythonOperator(
        task_id="run_review_analysis",
        python_callable=run_review_analysis,
    )

    # 병렬 실행
    [t_hidden_gems, t_genre_stats, t_review_analysis]