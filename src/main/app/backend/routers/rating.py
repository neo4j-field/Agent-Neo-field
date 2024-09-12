from database.communicator import GraphWriter
from fastapi import APIRouter, Depends
from objects.rating import Rating
from tools.secret_manager import EnvSecretManager, SecretManager

secret_manager = EnvSecretManager(env_path=".env")
router = APIRouter()


def get_writer(sm: SecretManager):
    writer = GraphWriter(secret_manager=sm)
    try:
        yield writer
    finally:
        writer.close_driver()


@router.post("/rating")
async def rate_message(
    rating: Rating,
    writer: GraphWriter = Depends(
        lambda: get_writer(EnvSecretManager(env_path=".env"))
    ),
) -> None:
    """
    Write a message rating to the database.
    """

    writer.rate_message(rating=rating)
