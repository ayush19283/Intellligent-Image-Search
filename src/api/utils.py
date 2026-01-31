import os
import pika
from src.db.database import get_db
from src.db import models, database
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import os



model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

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

    key = channel.queue_declare(queue=chName)

    channel.basic_publish(exchange='',
                      routing_key=chName,
                      body=message)

def TriggerImageProcessingJob(imageId: int, db):


    job = models.Job(FileId = imageId, FaceEncodingStatus = 'pending', UniversalEncodingStatus = 'pending')
    db.add(job)
    db.commit()

    TriggerQueue("clip_processor",str(imageId))
    TriggerQueue("face_encoder",str(imageId))


def GetEmbedding(querry: str):

    return generate_encoding_for_channel(querry)


def generate_encoding_for_channel(ch, method, properties, body):
    print("Received message for generating CLIP encoding", body)

    embeddings = encode_text(text=body.decode('utf-8'))
    return embeddings
   

def encode_text(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    outputs = model.get_text_features(**inputs)
    return outputs[0].detach().cpu().numpy().tolist()

    


    

    