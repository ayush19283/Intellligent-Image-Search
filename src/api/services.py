from sqlalchemy.orm import Session
from src.db import models
from fastapi import UploadFile
from datetime import datetime
import utils

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

async def uploadFile(db: Session, uploadedfile: UploadFile):
    if not uploadedfile:
        return {"error":"No file attached"}
    else:
        with open(f"uploads/{datetime.now()}.png","wb") as f:
            f.write(await uploadedfile.read())

        file = models.File(Name = uploadedfile.filename, Url = f"uploads/{datetime.now()}.png")

        db.add(file)
        db.commit()
        db.refresh(file)

        utils.TriggerImageProcessingJob(file.ID,db)
       
        return {"file recived",uploadedfile.filename}
