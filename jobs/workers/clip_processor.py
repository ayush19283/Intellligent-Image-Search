from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import db_client 
import requests
import io
import json

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
redis_client = db_client.get_redis_client()


def encode_image(image):
    inputs = processor(images=image, return_tensors = "pt")
    outputs = model.get_image_features(**inputs)
    return outputs[0].detach().cpu().numpy().tolist()

def encode_text(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    outputs = model.get_text_features(**inputs)
    return outputs[0].detach().cpu().numpy().tolist()

def process_image(ch, method, properties, body):
    print("Received message for encoding image", body)
    job_id = int(body)
    conn, cur = db_client.get_conn()
    cur.execute(
        "Select Url, files.ID from files JOIN jobs ON files.ID = job.fileID WHERE" \
         "jobs.ID == %s AND jobs.UniversalEncodingStatus == 'pending'",(job_id,)
    )

    job = cur.fetchone()

    if not job:
        print(f"No pending job found with id {job_id}")
        return
    
    file_url = job["Url"]
    image_response = requests.get(file_url)
    image_bytes = image_response.content
    image = Image.open(io.BytesIO(image_bytes))

    image_embeddings = encode_image(image)

    cur.execute("UPDATE jobs SET universal_encoding_status = 'completed' WHERE id = %s", (job_id,))
    conn.commit()

    cur.execute("Update files SET embedding = %s where fileID = %s",(image_embeddings, job['fileID']))
    conn.commit()
    return

def generate_encoding_for_channel(ch, method, properties, body):
    print("Received message for generating CLIP encoding", body)

    embeddings = encode_text(text=body.decode('utf-8'))
    return embeddings
    # if not embeddings:
    #     print(f"Failed to generate embeddings for text: {body.decode('utf-8')}")
    #     redis_client.publish('encoding_results', json.dumps({
    #         'embeddings': None
    #     }))
    #     return
    
    # print(embeddings)
    # redis_client.publish('encoding_results', json.dumps({
    #     'embeddings': embeddings
    # }))