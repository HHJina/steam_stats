import pytest

from collector.kafka.producer import SteamProducer
from collector.steam.client import SteamClient
from collector.steam.parser import (
    parse_game,
    parse_genres,
    parse_price,
    parse_review_snapshot,
    parse_reviews,
)

@pytest.fixture
def client():
    return SteamClient()

@pytest.fixture
def raw_game(client):
    return client.steam_app_detail(1245620)

@pytest.fixture
def raw_reviews(client):
    return client.get_reviews(1245620)

@pytest.fixture
def producer():
    return SteamProducer()

# client 테스트
def test_steam_app_detail(client):
    data = client.steam_app_detail(730)
    assert data["steam_appid"] == 730
    assert "name" in data

def test_invalid_app_id(client):
    with pytest.raises(ValueError):
        client.steam_app_detail(999999999)

def test_top_rank_games(client):
    ranks = client.top_rank_games()
    assert len(ranks) == 100
    assert "appid" in ranks[0]
    assert "concurrent_in_game" in ranks[0]


# parser 테스트
def test_parse_game(raw_game):
    game = parse_game(raw_game, 100000)
    assert game["app_id"] == 1245620
    assert game["name"] is not None

def test_parse_genres(raw_game):
    genres = parse_genres(raw_game)
    assert isinstance(genres, list)
    assert len(genres) > 0

def test_parse_price(raw_game):
    price = parse_price(raw_game)
    assert "price" in price
    assert "discount_rate" in price

def test_parse_review_snapshot(raw_reviews):
    snapshot = parse_review_snapshot(raw_reviews, 1245620)
    assert snapshot["total_reviews"] > 0
    assert snapshot["positive_reviews"] >= 0
    assert snapshot["negative_reviews"] >= 0

def test_parse_reviews(raw_reviews):
    reviews = parse_reviews(raw_reviews, 1245620)
    assert len(reviews) > 0
    assert "review_id" in reviews[0]
    assert "review_text" in reviews[0]

# producer 테스트
def test_send_game(producer, raw_game):
    game = parse_game(raw_game, 100000)
    # 에러 없이 전송되면 성공
    producer.send_game(game)
    producer.flush()

def test_send_genres(producer, raw_game):
    genres = parse_genres(raw_game)
    producer.send_genres({"app_id": 1245620, "genres": genres})
    producer.flush()

def test_send_price(producer, raw_game):
    price = parse_price(raw_game)
    producer.send_price(price)
    producer.flush()

def test_send_review_snapshot(producer, raw_reviews):
    snapshot = parse_review_snapshot(raw_reviews, 1245620)
    producer.send_review_snapshot(snapshot)
    producer.flush()

def test_send_review(producer, raw_reviews):
    reviews = parse_reviews(raw_reviews, 1245620)
    producer.send_review(reviews[0])
    producer.flush()