"""Application configuration. Values come from environment variables / .env."""
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def _db_uri() -> str:
    # SQLite is the default so the project runs locally without a MySQL server.
    # To use MySQL instead, set DATABASE_URL in your .env file.
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    user = os.getenv("DB_USER", "root")
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "placement_db")
    if os.getenv("DB_HOST") or os.getenv("DB_NAME") or os.getenv("DB_PASSWORD"):
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"
    return "sqlite:///dev.db"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me")
    SQLALCHEMY_DATABASE_URI = _db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB upload limit

    # Configurable criteria used by the "Placement Preparation Insights" module
    PREP_RULES = {
        "min_cgpa": 6.5,
        "max_backlogs": 0,
        "min_aptitude": 60,
        "min_skills": 4,
        "min_internships": 1,
        "min_certifications": 1,
        "required_skills": ["python", "sql"],
    }
