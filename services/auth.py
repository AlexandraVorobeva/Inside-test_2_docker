from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi_sqlalchemy import db
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from jose import JWTError, jwt
from pydantic import ValidationError
from schema.auth import UserCreate
import models
from schema.auth import User, Token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/sign-in/")


def verify_token(token: str) -> User:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            key="4yIsAPEHcuV07VVlEEaAb5ddYhpjhOK0pVcolC1pZlo",
            algorithms=["HS256"],
        )
    except JWTError:
        raise exception from None

    user_data = payload.get("user")

    try:
        user = User.parse_obj(user_data)
    except ValidationError:
        raise exception from None

    return user


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return verify_token(token)


def create_token(user: models.User) -> Token:
    """
    Create token for user.
    :param user: name of user
    :return: token
    """
    user_data = User.from_orm(user)
    now = datetime.utcnow()
    payload = {
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(seconds=3600),
        "sub": str(user_data.id),
        "user": user_data.dict(),
    }
    key = "4yIsAPEHcuV07VVlEEaAb5ddYhpjhOK0pVcolC1pZlo"
    token = jwt.encode(
        payload,
        key=key,
        algorithm="HS256",
    )
    return Token(access_token=token)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    Create hash for a password.
    :param password: password
    :return: hash
    """
    return bcrypt.hash(password)


def register_new_user(user_data: UserCreate) -> Token:
    user = models.User(
        username=user_data.username, password_hash=hash_password(user_data.password)
    )
    db.session.add(user)
    db.session.commit()
    return create_token(user)


def authenticate_user(username: str, password: str) -> Token:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = (
        db.session.query(models.User).filter(models.User.username == username).first()
    )

    if not user:
        raise exception

    if not verify_password(password, user.password_hash):
        raise exception

    return create_token(user)


def get_all():
    users = db.session.query(models.User).all()
    return users
