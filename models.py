from sqlalchemy import Column, Integer, String, Text, DateTime
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