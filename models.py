from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from database import Base

class Resume(Base):
    # The actual table name that will be created in PostgreSQL
    __tablename__ = "resumes"

    # Each line below is one COLUMN in the table.
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    page_count = Column(Integer)
    word_count = Column(Integer)
    character_count = Column(Integer)
    extracted_text = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)