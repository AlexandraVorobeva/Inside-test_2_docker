from pydantic import BaseModel


class BaseMessege(BaseModel):
    username: str
    message: str


class Message(BaseMessege):
    id: int

    class Config:
        orm_mode = True


class MessageCreate(BaseMessege):
    pass
