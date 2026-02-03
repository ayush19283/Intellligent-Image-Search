from sqlalchemy.orm import Session
from sqlalchemy import text
from src.db import models
from fastapi import UploadFile, Depends, HTTPException
from datetime import datetime
from .utils import TriggerImageProcessingJob, GetEmbedding, get_password_hash, verify_password, create_access_token,get_current_user
import uuid
from pwdlib import PasswordHash
from typing import Annotated
import os
import jwt
from typing import List
from .schema import TagPhotos

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def signup(db: Session, email: str, password: str, name: str=""):
    usr = models.User
    exists = db.query(usr).filter(usr.email == email).first()

    if exists:
        return {"error": "email already exists"}

    user = usr(email = email, password = get_password_hash(password), name = name)


    db.add(user)
    db.commit()
    db.refresh(user)
    data = {"sub": str(exists.id)}
    token = create_access_token(data)

    return {"id": user.id, "email": user.email, "token": token}

def signin(db: Session, email: str, password: str):
    usr = models.User
    exists = db.query(usr).filter(usr.email == email).first()

    if exists:
        if(verify_password(password, exists.password)):
            data = {"sub": str(exists.id)}
            token = create_access_token(data)
            return {"id": exists.id, "email": exists.email, "token":token}
        else:
            return {"error": "wrong password"}
    
    return {"error": "email not found"}

async def uploadFile(db: Session, uploadedfile: UploadFile, token):
    print("token",token)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    print("username", username)
    if not uploadedfile:
        return {"error":"No file attached"}
    unique_file_name = str(uuid.uuid4())
    with open(f"uploads/{unique_file_name}.png","wb") as f:
        f.write(await uploadedfile.read())

    file = models.File(name = uploadedfile.filename, url = f"uploads/{unique_file_name}.png", user_id = username)

    db.add(file)
    db.commit()
    db.refresh(file)

    print("received file - invoking queue")

    TriggerImageProcessingJob(file.id,db)
    
    return {"file":uploadedfile.filename}
    
def getFile(db: Session, querry: str, token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    if querry:
        embedding = GetEmbedding(querry)
        result = db.execute(
            text(f"SELECT id, name, url FROM files WHERE user_id = {username} ORDER BY embedding <=> '{embedding}' LIMIT 5")
        ).mappings().all()
        return {"embeddings":result}
    
def getUnknownFaces(db: Session, token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    result = db.query(models.Face, models.UniqueFace, models.File).\
        join(models.UniqueFace, models.Face.unique_face_id == models.UniqueFace.id).\
        join(models.File, models.Face.file_id == models.File.id).\
        filter(models.File.user_id == username).all()

    if result:
    # Return a list of dictionaries with image URLs
        return {"image_urls": [face.url for face in result]}
    else:
        raise HTTPException(status_code=404, detail="No faces found for this user")

def tagFaces(body: List[TagPhotos],db: Session, token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    for uf in body:
        print("name and id", uf.image_id, uf.unique_name)
        
        update_result = db.query(models.UniqueFace).filter(models.UniqueFace.id == uf.image_id).update(
            {'name': uf.unique_name}
        )
        
        if update_result == 0:
            raise HTTPException(status_code=404, detail=f"UniqueFace with ID {uf.image_id} not found")
        
    db.commit()
    
    return {"staus":"uploaded successfully"}
    


# def getUnknownFaces(db: Session):