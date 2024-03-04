from fastapi import APIRouter

from database.communicator import GraphWriter
from objects.rating import Rating

router = APIRouter()
writer = GraphWriter()


@router.post("/rating")
async def rate_message(rating: Rating) -> None:
    """
    Write a message rating to the database.
    """

    writer.rate_message(rating=rating)
