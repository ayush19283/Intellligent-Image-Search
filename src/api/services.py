from sqlalchemy.orm import Session
from src.db import models
from fastapi import UploadFile

def signup(db: Session, email: str, password: str, name: str=""):
    usr = models.User
    exists = db.query(usr).filter(usr.Email == email).first()

    if exists:
        return {"error": "email already exists"}
    
    user = usr(Email = email, Password = password, Name = name)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.ID, "email": user.Email}

def signin(db: Session, email: str, password: str):
    usr = models.User
    exists = db.query(usr).filter(usr.Email == email).first()

    if exists:
        if(exists.Password == password):
            return {"id": exists.ID, "email": exists.Email}
        else:
            return {"error": "wrong password"}
    
    return {"error": "email not found"}

def uploadFile(db: Session, file: UploadFile):
    if not file:
        return {"error":"No file attached"}
    else:
        return {"file recived",file.filename}
