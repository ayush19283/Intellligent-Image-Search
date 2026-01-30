from fastapi import FastAPI, APIRouter, Depends, UploadFile
from .services import signup, signin, uploadFile
from .schema import SignInRequest, SignUpRequest
from src.db.database import get_db
from sqlalchemy.orm import Session


app = FastAPI()
router = APIRouter()

@router.post("/signup")
def SignUp(request : SignUpRequest, db: Session = Depends(get_db)):
    return signup(db, request.email,request.password,request.name)

@router.post("/signin")
def SingIn(request : SignInRequest, db:Session = Depends(get_db)):
    return signin(db, request.email,request.password)
   
@router.post("/upload")
async def UploadFile(file : UploadFile, db: Session = Depends(get_db)):
    return await uploadFile(db,file)

