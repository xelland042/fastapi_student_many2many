import secrets
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from jwt_handlers import get_password_hash, signJWT, verify_password
from models import get_db, User

router = APIRouter()

security = HTTPBasic()


class UserSignUpSchema(BaseModel):
    username: str
    first_name: str = Field(default=None)
    last_name: str = Field(default=None)
    email: EmailStr
    password_1: str
    password_2: str


class UserLoginScheme(BaseModel):
    username: str
    password: str


def get_current_username(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
        db: Session = Depends(get_db)
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = db.query(User).get(str(current_username_bytes))
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = db.query(User).get(str(current_password_bytes))
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def check_user_signup(data: UserSignUpSchema, db: Session):
    user = db.query(User).filter(User.username == data.username).first()
    if user and verify_password(data.password_1, user.hashed_password) and data.email == user.email:
        return True
    return False


@router.get("/users/login/")
def read_current_user(username: Annotated[str, Depends(get_current_username)]):
    return {"username": username}


@router.post('/user/signup/', tags=['Users'])
async def user_signup(user: UserSignUpSchema, db: Session = Depends(get_db)):
    if user.password_1 != user.password_2:
        raise HTTPException(detail='Passwords should be same!', status_code=status.HTTP_400_BAD_REQUEST)
    if check_user_signup(user, db):
        raise HTTPException(detail='User already exist!', status_code=status.HTTP_400_BAD_REQUEST)
    else:
        hashed_pwd = get_password_hash(user.password_1)
        user = User(username=user.username, first_name=user.first_name, last_name=user.last_name,
                    hashed_password=hashed_pwd, email=user.email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {**signJWT(user.email), 'username': user.username, 'first_name': user.first_name,
                'last_name': user.last_name, 'email': user.email}
