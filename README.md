# Photo Search System with CLIP and Face Recognition

This project allows users to upload photos to the server, which are processed using **CLIP** for image embedding and **Face Recognition** for identifying unique faces and their locations in the images. The processed data enables efficient searching of photos based on specific queries, such as finding images with a person wearing a red t-shirt or searching by unique faces.

## Features

- **Upload Images**: Users can upload images directly to the server.
- **Image Processing**:
  - **CLIP (Contrastive Language-Image Pretraining)**: Generates embeddings for each image, which are used for content-based search.
  - **Face Recognition**: Identifies and labels unique faces in the images along with their locations.
- **Search Based on Queries**: 
  - Search images based on text queries such as "person with red t-shirt".
  - Retrieve images using face recognition features (e.g., identifying images of a specific person).
- **Message Queue**: Utilizes **RabbitMQ** for message queuing to handle asynchronous tasks efficiently.

## Tech Stack

- **CLIP** (Contrastive Language-Image Pretraining) for image-text matching and embeddings.
- **Face Recognition** for identifying faces and extracting facial features.
- **RabbitMQ** for message queuing to handle asynchronous tasks efficiently.
- **Python**: Core language for implementing the logic and processing.
- **FastAPI**: For handling image uploads and API requests.
  
## Setup

### Prerequisites

1. Python 3.12
2. RabbitMQ server
3. Required Python packages:
    - `clip-vit-pytorch`
    - `face_recognition`
    - `pika` (for RabbitMQ)
    - `FastAPI`

### Installation

1. **Clone the repository**:
   git clone https://github.com/ayush19283/Intellligent-Image-Search.git
   cd Intellligent-Image-Search

2. **Install required dependencies:**:
    pip install -r requirements.txt

3. **Start RabbitMQ**
    cd jobs
    python consumer.py

4. **Run the server:**
    python app.py  