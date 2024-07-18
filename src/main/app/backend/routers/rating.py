from fastapi import APIRouter, Depends

from database.communicator import GraphWriter
from objects.rating import Rating
from tools.secret_manager import SecretManager,GoogleSecretManager,EnvSecretManager

secret_manager = EnvSecretManager(env_path='.env')
router = APIRouter()
writer = GraphWriter(secret_manager)



def get_writer():
    writer = GraphWriter(secret_manager=sm)
    try:
        yield writer
    finally:
        writer.close_driver()


@router.post("/rating")
async def rate_message(
    rating: Rating, writer: GraphWriter = Depends(get_writer)
) -> None:
    """
    Write a message rating to the database.
    """

    writer.rate_message(rating=rating)
