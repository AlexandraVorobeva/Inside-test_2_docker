import os
import uvicorn
from typing import List
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_sqlalchemy import DBSessionMiddleware
from dotenv import load_dotenv

from schema.messages import Message, MessageCreate
from schema.auth import User, UserCreate, Token
from services.messages import create_message, get_history_of_mes
from services.auth import (
    register_new_user,
    authenticate_user,
    get_current_user,
)

load_dotenv(".env")

app = FastAPI(title="Inside", description="API by Aexandra Vorobeva")

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])


@app.post("/sign-up/", response_model=Token)
def sign_up(user_data: UserCreate):
    return register_new_user(user_data)


@app.post("/sign-in/", response_model=Token)
def sign_in(form_data: OAuth2PasswordRequestForm = Depends()):
    return authenticate_user(
        form_data.username,
        form_data.password,
    )


@app.post("/create_message", response_model=Message)
def post_message(
    message_data: MessageCreate,
    user: User = Depends(get_current_user),
):
    return create_message(message_data)


@app.get("/{username}/", response_model=List[Message])
def get_history_of_messages(
        username: str,
        history_of_message: str,
        user: User = Depends(get_current_user),
):
    return get_history_of_mes(username, history_of_message)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
