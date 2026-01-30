from pydantic import BaseModel

class SignUpRequest(BaseModel):
    name : str
    email : str
    password : str

class SignInRequest(BaseModel):
    email : str
    password : str