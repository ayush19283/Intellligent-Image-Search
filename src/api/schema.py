from pydantic import BaseModel

class SignUpRequest(BaseModel):
    name : str
    email : str
    password : str

class SignInRequest(BaseModel):
    email : str
    password : str

class TagPhotos(BaseModel):
    image_id : str
    unique_name : str