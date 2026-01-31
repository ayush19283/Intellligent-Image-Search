import pika
import workers.clip_processor as clip_processor
import workers.face_encoder as face_encoder
import os


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
    channel = connection.channel()


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

    channel.queue_declare(queue='generate_clip_encoding')
    channel.basic_consume(queue='generate_clip_encoding',
                    auto_ack=True,
                    on_message_callback=clip_processor.generate_encoding_for_channel
                    )
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')