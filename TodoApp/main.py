from fastapi import FastAPI, Depends, HTTPException, Path, Query
import models 
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from starlette import status
from pydantic import BaseModel, Field
from routers import auth, todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todos.router)




