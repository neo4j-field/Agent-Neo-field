from fastapi import APIRouter

from database.communicator import GraphWriter
from objects.rating import Rating
from tools.secret_manager import SecretManager,GoogleSecretManager,EnvSecretManager

secret_manager = EnvSecretManager(env_path='.env')
router = APIRouter()
writer = GraphWriter(secret_manager)


@router.post("/rating")
async def rate_message(rating: Rating) -> None:
    """
    Write a message rating to the database.
    """

    writer.rate_message(rating=rating)
