import face_recognition
import db_client
import requests
import io
import os
import PIL.Image as Image
import secrets


def encodeFace(image):
    image = face_recognition.load_image_file(image)

    # Encode the face(s)
    face_encodings = face_recognition.face_encodings(image, num_jitters=10, model="large")
    face_locations = face_recognition.face_locations(image)
    return face_encodings, face_locations if face_encodings else ([], [])

def process_image(ch, method, properties,body):
    job_id = int(body)
    conn, cur = db_client.get_conn()

    cur.execute("SELECT file_id, url from files JOIN Jobs ON files_id = Jobs.file_id WHERE jobs.id == %s AND job.face_encoding_status = 'pending'",(job_id,))

    job = cur.fetchone()
    if not job:
        print(f"No pending job found with id {job_id}")
        return
    file_url = job.get('url')

    response = requests.get(file_url)
    image = io.BytesIO(response.content)
    face_encodings = encodeFace(image)

    if not face_encodings:
        cur.execute("Update jobs SET face_encoding_status = 'failed' WHERE id = %s",(job_id,))
        conn.commit()
        print(f"No faces found in image for job id {job_id}")
        return
    
    print(f"Found {len(face_encodings)} face(s) in image for job id {job_id}")

    for encoding, location in zip(face_encodings):

        cur.execute(
            "Select id, embedding <-> %s as distance FROM unique_faces " \
            "where embedding <-> %s < %s ORDER BY distance ASC LIMIT 1",( str(encoding.tolist()), str(encoding.tolist()), float(os.getenv("FACE_ENCODING_THRESHOLD") ) )
        )

        result = cur.fetchone()

        if result:
            uniqueFaceId = result[1]
        else:
            top, right, bottom, left = location
            image = io.BytesIO(response.content)
            image = Image.open(image)
            face_image = image.crop((left, top, right, bottom))
            face_image_io = io.BytesIO()
            face_image.save(face_image_io, format='JPEG')
            face_image_io.seek(0)
            filename = f'face_{job_id}_{secrets.token_hex(16)}.jpg'
            with open(f'../uploads/faces/{filename}', 'wb') as f:
                f.write(face_image_io.read())
            url = f'{os.getenv("SERVER_HOST")}/api/files/download/faces/{filename}'
        
            cur.execute(
                "INSERT into unique_face (embedding, url) VALUES (%s, %s) RETURNING id", 
                (str(encoding.tolist()), url)        
            )    
            uniqueFaceId = cur.fetchone()['id']

        cur.execute(
            "INSERT INTO faces (file_id, unique_face_id, coordinates) VALUES (%s, %s, %s)",
            (job['id'], uniqueFaceId, list(location))
        )

    cur.execute("UPDATE jobs SET face_encoding_status = 'completed' WHERE id = %s", (job_id,))
    conn.commit()
    print(f"Successfully processed job id {job_id}")