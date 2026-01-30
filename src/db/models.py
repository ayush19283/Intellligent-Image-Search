from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Column, Integer, Text, DateTime, ForeignKey, Float, func
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    ID = Column(Integer,primary_key=True)
    Name = Column(String(50))
    Email = Column(String(120),unique=True)
    Password = Column(Text)
    CreatedAt = Column(DateTime)
    
class File(Base):
    __tablename__ = "files"

    ID = Column(Integer,primary_key=True)
    Name = Column(String(120),unique=True)
    Description = Column(String(512))
    UploadedAt = Column(DateTime, default = func.now())
    Embedding = Column(Vector(512))

    UserId = Column(Integer, ForeignKey("user.ID"))

class Job(Base):
    __tablename__ = "jobs"

    ID = Column(Integer, primary_key=True)
    FileId = Column(Integer,ForeignKey("files.ID"))
    StartedAt = Column(DateTime)
    EndedAt = Column(DateTime)
    FaceEncodingStatus = Column(DateTime)
    UniversalEncodingStatus = Column(String(50))


class UniqueFace(Base):
    __tablename__ = "unique_faces"

    ID = Column(Integer, primary_key=True)
    Name = Column(String(50), nullable=False)
    Coordinates = Column(ARRAY(Float))
    

class Face(Base):
    __tablename__ = "faces"

    ID = Column(Integer, primary_key=True)
    FileId = Column(Integer, ForeignKey("files.ID"))
    UniqueFaceId = Column(Integer, ForeignKey("unique_faces.ID"))
    Coordinates = Column(ARRAY(Float))


