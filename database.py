from dotenv import load_dotenv
load_dotenv()
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection string from .env (keeps the password out of our code)
DATABASE_URL = os.getenv("DATABASE_URL")

  # The engine is the core link to the database.
engine = create_engine(DATABASE_URL)

  # A session = one conversation with the DB (one set of reads/writes).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

  # Base is the parent class our table models inherit from (used in models.py).
Base = declarative_base()

  # Gives an endpoint a database session, then closes it when done.
  # FastAPI calls this automatically for any endpoint that asks for `db`.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()