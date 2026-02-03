from fastapi import FastAPI, APIRouter, Depends, UploadFile
from .services import signup, signin, uploadFile, getFile
from .schema import SignInRequest, SignUpRequest
from src.db.database import get_db
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from src.db import models
from datetime import datetime, timedelta, timezone
from .utils import authenticate_user, create_access_token, get_current_user



app = FastAPI()
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/signup")
def SignUp(request : SignUpRequest, db: Session = Depends(get_db)):
    return signup(db, request.email,request.password,request.name)

@router.post("/signin")
def SingIn(request : SignInRequest, db:Session = Depends(get_db)):
    return signin(db, request.email,request.password)
   
@router.post("/upload")
async def UploadFile(file : UploadFile, token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    return await uploadFile(db,file,token)

@router.get("/image")
def GetFiles(querry: str, 
             token: Annotated[str, Depends(oauth2_scheme)],
             db: Session = Depends(get_db)
             ):
    return getFile(db, querry,token)


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db:Session = Depends(get_db)
) -> Token:
    user = authenticate_user(db = db, username = form_data.username, password = form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=1440)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

# @router.get("unknown-faces")
# def GetUnknownFaces():

