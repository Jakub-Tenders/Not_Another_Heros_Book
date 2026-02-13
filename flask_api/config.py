import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:0000@localhost:5432/storyline"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.getenv("FLASK_API_KEY", "")