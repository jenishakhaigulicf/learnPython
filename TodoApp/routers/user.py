from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path, Query
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

import models
from database import SessionLocal, engine
from models import Users
from routers import auth

from .auth import CreateUserRequest, UpdateUserPhoneNumberReq, get_current_user

app = FastAPI()
router = APIRouter(prefix="/user", tags=["user"])

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
    db: db_dependency,
    create_user_request: CreateUserRequest,
    user_id: int = Query(gt=0),
):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_model.email = create_user_request.email
    user_model.first_name = create_user_request.first_name
    user_model.last_name = create_user_request.last_name
    user_model.hashed_password = bcrypt_context.hash(create_user_request.password)
    user_model.role = create_user_request.role

    db.add(user_model)
    db.commit()


@router.put("/phone-number", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_phone_number(
    db: db_dependency,
    update_phone_number_request: UpdateUserPhoneNumberReq,
    user_id: int = Query(gt=0),
):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    print("--->", user_model.__dict__, user_model.phone_number is not None)
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    if (
        user_model.phone_number != update_phone_number_request.old_phone_number
        and user_model.phone_number is not None
    ):
        raise HTTPException(status_code=404, detail="Phone number incorrect")
    user_model.phone_number = update_phone_number_request.new_phone_number
    db.commit()
    db.refresh(user_model)
    return user_model
