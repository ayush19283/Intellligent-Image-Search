import os
import pika
from src.db.database import get_db
from src.db import models, database
from jobs.workers.clip_processor import generate_encoding_for_channel

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
                      routing_key=key,
                      body=message)

def TriggerImageProcessingJob(imageId: int, db):
    

    job = models.Job(FileId = imageId, FaceEncodingStatus = 'pending', UniversalEncodingStatus = 'pending')
    db.add(job)
    db.commit()

    TriggerQueue("clip_processor",str(imageId))
    TriggerQueue("face_encoder",str(imageId))


def GetEmbedding(querry: str):

    return generate_encoding_for_channel(querry)




    



    


    

    