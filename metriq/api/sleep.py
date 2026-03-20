from fastapi import APIRouter
from metriq.services.sleep_score import calculate_sleep_score

router = APIRouter()

@router.get("/sleep_score")
def sleep_score():
    return calculate_sleep_score()