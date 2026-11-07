from typing import List, Literal

from pydantic import BaseModel, Field


class SwipeRequest(BaseModel):
    swiper_id: str = Field(min_length=1)
    swipee_id: str = Field(min_length=1)
    direction: Literal["left", "right"]


class SwipeResponse(BaseModel):
    swiper_id: str
    swipee_id: str
    direction: str
    matched: bool


class Match(BaseModel):
    user_id: str
    matched_at: str


class MatchesResponse(BaseModel):
    user_id: str
    matches: List[Match]
