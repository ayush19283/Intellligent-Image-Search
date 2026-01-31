from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import requests
import io
import json
import os
import redis
import db_client

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_redis_client():
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    print("Connecting to Redis server...", REDIS_HOST, REDIS_PORT)
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    return redis.from_url(redis_url)

redis_client = get_redis_client()

def encode_image(image):
    inputs = processor(images=image, return_tensors = "pt")
    outputs = model.get_image_features(**inputs)
    return outputs[0].detach().cpu().numpy().tolist()


def process_image(ch, method, properties, body):
    print("Received message for encoding image", body)
    job_id = int(body)
    conn, cur = db_client.get_conn()
    cur.execute(
        "Select url, files.id from files JOIN jobs ON files.id = job.file_id WHERE " \
         "jobs.id == %s AND jobs.universal_encoding_status == 'pending'",(job_id,)
    )

    job = cur.fetchone()

    if not job:
        print(f"No pending job found with id {job_id}")
        return
    
    file_url = job["url"]
    image_response = requests.get(file_url)
    image_bytes = image_response.content
    image = Image.open(io.BytesIO(image_bytes))

    image_embeddings = encode_image(image)

    cur.execute("UPDATE jobs SET universal_encoding_status = 'completed' WHERE id = %s", (job_id,))
    conn.commit()

    cur.execute("Update files SET embedding = %s where file_id = %s",(image_embeddings, job['file_id']))
    conn.commit()
    return

