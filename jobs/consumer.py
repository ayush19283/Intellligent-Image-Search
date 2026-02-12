import dotenv
import pika
import workers.clip_processor as clip_processor
import workers.face_encoder as face_encoder
import os
from kafka import KafkaConsumer
dotenv.load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                username=RABBITMQ_USER,
                password=RABBITMQ_PASSWORD
            )   
    ))

    consumer = KafkaConsumer(
        'clip_processor',
        group_id = "clip_consumer_group",
        bootstrap_servers = ['localhost:9092'],
        auto_offset_reset = 'earliest',
        value_deserializer = lambda x: x.decoder('utf-8')
    )

    channel = connection.channel()

    for msg in consumer:

        job_id = msg.value.get('job_id',None)
        if job_id is not None:
           print(f"Consumed Job ID: {job_id}")
        else:
            print("No job ID in message")



    channel.queue_declare(queue='clip_processor')
    channel.basic_consume(queue='clip_processor',
                        auto_ack=True,
                        on_message_callback = clip_processor.process_image
                        )

    channel.queue_declare(queue='face_encoder')
    channel.basic_consume(queue='face_encoder',
                        auto_ack=True,
                        on_message_callback = face_encoder.process_image
                        )

    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')