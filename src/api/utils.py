import os
import pika
from src.db.database import get_db
from src.db import models, database
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import os
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import jwt
from pydantic import BaseModel
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from src.db import models


password_hash = PasswordHash.recommended()
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    id: str | None = None


def TriggerQueue(chName, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                username=RABBITMQ_USER,
                password=RABBITMQ_PASSWORD
            )   
    ))
    channel = connection.channel()

    channel.queue_declare(queue=chName)

    channel.basic_publish(exchange='',
                      routing_key=chName,
                      body=message)

def TriggerImageProcessingJob(imageId: int, db):


    job = models.Job(file_id = imageId, face_encoding_status = 'pending', universal_encoding_status = 'pending')
    db.add(job)
    db.commit()
    print("started with job id",job.id)
    TriggerQueue("clip_processor",str(job.id))
    TriggerQueue("face_encoder",str(job.id))


def GetEmbedding(querry: str):
    return generate_encoding_for_channel(body = querry)


def generate_encoding_for_channel(**kwargs):
    querry = kwargs["body"]
    print("Received message for generating CLIP encoding", querry)
    embeddings = encode_text(text = querry)
    return embeddings
   

def encode_text(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    outputs = model.get_text_features(**inputs)
    return outputs[0].detach().cpu().numpy().tolist()

    

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Session = Depends(get_db),):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        print("user id get curr user", user_id)
    except InvalidTokenError:
        raise credentials_exception
    user = db.query(models.User).filter(id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(username: str, password: str, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user