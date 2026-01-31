from sqlalchemy.orm import Session
from src.db import models
from fastapi import UploadFile
from datetime import datetime
from .utils import TriggerImageProcessingJob

def signup(db: Session, email: str, password: str, name: str=""):
    usr = models.User
    exists = db.query(usr).filter(usr.email == email).first()

    if exists:
        return {"error": "email already exists"}
    
    user = usr(email = email, password = password, name = name)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "email": user.email}

def signin(db: Session, email: str, password: str):
    usr = models.User
    exists = db.query(usr).filter(usr.Email == email).first()

    if exists:
        if(exists.Password == password):
            return {"id": exists.id, "email": exists.email}
        else:
            return {"error": "wrong password"}
    
    return {"error": "email not found"}

async def uploadFile(db: Session, uploadedfile: UploadFile):
    if not uploadedfile:
        return {"error":"No file attached"}
    else:
        with open(f"uploads/{datetime.now()}.png","wb") as f:
            f.write(await uploadedfile.read())

        file = models.File(name = uploadedfile.filename, url = f"uploads/{datetime.now()}.png", user_id = 1)

        db.add(file)
        db.commit()
        db.refresh(file)

        print("received file - invoking queue")

        TriggerImageProcessingJob(file.id,db)
       
        return {"file":uploadedfile.filename}
