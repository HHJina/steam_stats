.PHONY: up down restart logs ps clean run-api install lint format typecheck security test check

# 기본 개발 (DB + Redis만)
up-minimal:
	docker compose up -d postgresql redis

# 파이프라인 개발할 때 (Kafka 추가)
up-pipeline:
	docker compose up -d postgresql redis kafka

# 인프라 실행
up:
    docker compose up -d

# 인프라 종료
down:
	docker compose down

# 인프라 재시작
restart:
	docker compose down && docker compose up -d

# 로그 확인
logs:
	docker compose logs -f

# 서비스 상태 확인
ps:
	docker compose ps

# 볼륨까지 전부 삭제 (DB 초기화할 때)
clean:
	docker compose down -v

# API 서버 실행
run-api:
	uv run uvicorn api.main:app --reload

run:
	make run-api & cd frontend && npm run dev


# 의존성 설치
install:
	uv sync --all-extras --dev

# 린팅
lint:
	uv run ruff check .

# 포맷
format:
	uv run ruff format .

# 타입 체크
typecheck:
	uv run mypy api/

# 보안 스캔
security:
	uv run bandit -r api/ collector/

# 테스트
test:
	uv run pytest

# CI 로컬에서 전부 한번에 실행
check:
	uv run ruff check . && uv run ruff format --check . && uv run mypy api/ && uv run bandit -r api/ collector

fix:
	uv run ruff check --fix .
	uv run ruff format .

# 마이그레이션 파일 생성
migrate-create:
	alembic revision --autogenerate -m "$(msg)"

# DB에 적용
migrate:
    alembic upgrade head

# 한 단계 롤백
migrate-down:
    alembic downgrade -1

# PostgreSQL CLI 접속
db:
	docker exec -it steam_stats-postgresql-1 psql -U steam -d steamdb

# 테이블 목록 확인
db-tables:
	docker exec -it steam_stats-postgresql-1 psql -U steam -d steamdb -c "\dt"

# 전체 테스트
test:
	uv run pytest

# collector만 테스트
test-collector:
	uv run pytest tests/test_collector.py -v

kafka-init:
	docker exec -it steam_stats-kafka-1 kafka-topics --create --bootstrap-server kafka:9092 --topic steam-games --partitions 3 --replication-factor 1
	docker exec -it steam_stats-kafka-1 kafka-topics --create --bootstrap-server kafka:9092 --topic steam-genres --partitions 3 --replication-factor 1
	docker exec -it steam_stats-kafka-1 kafka-topics --create --bootstrap-server kafka:9092 --topic steam-prices --partitions 3 --replication-factor 1
	docker exec -it steam_stats-kafka-1 kafka-topics --create --bootstrap-server kafka:9092 --topic steam-players --partitions 3 --replication-factor 1
	docker exec -it steam_stats-kafka-1 kafka-topics --create --bootstrap-server kafka:9092 --topic steam-reviews --partitions 3 --replication-factor 1
	docker exec -it steam_stats-kafka-1 kafka-topics --create --bootstrap-server kafka:9092 --topic steam-review-snapshots --partitions 3 --replication-factor 1

kafka-topics:
	docker exec -it steam_stats-kafka-1 kafka-topics --list --bootstrap-server kafka:9092

kafka-delete:
	docker exec -it steam_stats-kafka-1 kafka-topics --delete --bootstrap-server kafka:9092 --topic steam-games
	docker exec -it steam_stats-kafka-1 kafka-topics --delete --bootstrap-server kafka:9092 --topic steam-genres
	docker exec -it steam_stats-kafka-1 kafka-topics --delete --bootstrap-server kafka:9092 --topic steam-prices
	docker exec -it steam_stats-kafka-1 kafka-topics --delete --bootstrap-server kafka:9092 --topic steam-players
	docker exec -it steam_stats-kafka-1 kafka-topics --delete --bootstrap-server kafka:9092 --topic steam-reviews
	docker exec -it steam_stats-kafka-1 kafka-topics --delete --bootstrap-server kafka:9092 --topic steam-review-snapshots

# Airflow DAG 목록 확인
airflow-dags:
	docker exec -it steam_stats-airflow-1 airflow dags list

# Airflow DAG 수동 실행
airflow-run:
	docker exec -it steam_stats-airflow-1 airflow dags trigger steam_collect_pipeline

airflow-trigger-analyze:
	docker exec -it steam_stats-airflow-1 airflow dags trigger steam_analyze_pipeline