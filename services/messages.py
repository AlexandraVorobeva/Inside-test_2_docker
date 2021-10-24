from fastapi import Depends, HTTPException, status
from fastapi_sqlalchemy import db
from schema.messages import MessageCreate
import models


def create_message(massage_data: MessageCreate) -> models.Message:
    message = models.Message(
        username=massage_data.username, message=massage_data.message
    )
    db.session.add(message)
    db.session.commit()
    return message


def get_history_of_mes(username: str, history_of_message: str) -> list[models.Message]:
    if history_of_message.split()[0] == "history":
        count = history_of_message.split()[1]
        messages = db.session.query(models.Message).filter(
            models.Message.username == username
        )
        mes = messages[:count]
        if not mes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return mes
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='History of messages must be like "history 10"',
    )
