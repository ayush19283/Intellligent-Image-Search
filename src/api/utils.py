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
    querry = kwargs["blue"]
    print("Received message for generating CLIP encoding", querry)
    embeddings = encode_text(text = querry)
    return embeddings
   

def encode_text(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    outputs = model.get_text_features(**inputs)
    return outputs[0].detach().cpu().numpy().tolist()

    


    

    