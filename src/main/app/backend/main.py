from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import llm, rating

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://chatbot.agent-neo-chat.com:8080",
    "https://chatbot.agent-neo-chat.com",
    "https://agent-neo-react-fe-qaiojvs3da-uc.a.run.app:8080",
    "https://agent-neo-react-fe-qaiojvs3da-uc.a.run.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm.router)
app.include_router(rating.router)
