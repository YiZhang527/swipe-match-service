def swipe(client, a, b, direction):
    return client.post("/swipes", json={"swiper_id": a, "swipee_id": b, "direction": direction})


def matches_of(client, user_id):
    resp = client.get(f"/users/{user_id}/matches")
    assert resp.status_code == 200
    return [m["user_id"] for m in resp.json()["matches"]]


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_one_way_right_swipe_no_match(client):
    resp = swipe(client, "alice", "bob", "right")
    assert resp.status_code == 201
    assert resp.json()["matched"] is False
    assert matches_of(client, "alice") == []


def test_mutual_right_swipe_creates_match(client):
    swipe(client, "alice", "bob", "right")
    resp = swipe(client, "bob", "alice", "right")
    assert resp.json()["matched"] is True
    assert matches_of(client, "alice") == ["bob"]
    assert matches_of(client, "bob") == ["alice"]


def test_left_swipe_never_matches(client):
    swipe(client, "alice", "bob", "right")
    resp = swipe(client, "bob", "alice", "left")
    assert resp.json()["matched"] is False
    assert matches_of(client, "alice") == []


def test_right_after_other_left_no_match(client):
    swipe(client, "alice", "bob", "left")
    resp = swipe(client, "bob", "alice", "right")
    assert resp.json()["matched"] is False


def test_repeat_swipe_no_duplicate_match(client):
    swipe(client, "alice", "bob", "right")
    swipe(client, "bob", "alice", "right")
    swipe(client, "bob", "alice", "right")
    assert matches_of(client, "alice") == ["bob"]


def test_multiple_matches(client):
    for other in ["bob", "carol"]:
        swipe(client, "alice", other, "right")
        swipe(client, other, "alice", "right")
    assert sorted(matches_of(client, "alice")) == ["bob", "carol"]


def test_cannot_swipe_self(client):
    assert swipe(client, "alice", "alice", "right").status_code == 400


def test_invalid_direction(client):
    assert swipe(client, "alice", "bob", "up").status_code == 422


def test_empty_user_id(client):
    assert swipe(client, "", "bob", "right").status_code == 422
