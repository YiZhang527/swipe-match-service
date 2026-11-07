from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from app import db
from app.models import Match, MatchesResponse, SwipeRequest, SwipeResponse

app = FastAPI(title="Swipe Match Service")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/swipes", response_model=SwipeResponse, status_code=201)
def create_swipe(req: SwipeRequest):
    if req.swiper_id == req.swipee_id:
        raise HTTPException(status_code=400, detail="Cannot swipe on yourself")

    now = datetime.now(timezone.utc).isoformat()
    db.put_swipe(req.swiper_id, req.swipee_id, req.direction, now)

    matched = False
    if req.direction == "right" and db.has_right_swiped(req.swipee_id, req.swiper_id):
        db.create_match(req.swiper_id, req.swipee_id, now)
        matched = True

    return SwipeResponse(**req.model_dump(), matched=matched)


@app.get("/users/{user_id}/matches", response_model=MatchesResponse)
def list_matches(user_id: str):
    items = db.get_matches(user_id)
    matches = [Match(user_id=i["match_user_id"], matched_at=i["matched_at"]) for i in items]
    return MatchesResponse(user_id=user_id, matches=matches)
