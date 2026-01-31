from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Column, Integer, Text, DateTime, ForeignKey, Float, func
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(120), unique=True)
    password = Column(Text)
    created_at = Column(DateTime)
    
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    description = Column(String(512))
    uploaded_at = Column(DateTime, default=func.now())
    embedding = Column(Vector(512))
    url = Column(Text)

    user_id = Column(Integer, ForeignKey("user.id"))

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, default=func.now())
    face_encoding_status = Column(String(50))
    universal_encoding_status = Column(String(50))


class UniqueFace(Base):
    __tablename__ = "unique_faces"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    embedding = Column(Vector(512))
    url = Column(Text)
    

class Face(Base):
    __tablename__ = "faces"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    unique_face_id = Column(Integer, ForeignKey("unique_faces.id"))
    coordinates = Column(ARRAY(Float))
