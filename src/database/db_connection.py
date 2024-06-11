import  os
from dotenv import load_dotenv


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings



load_dotenv()

# SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL')
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
        Get a database session (SQLAlchemy) for the request.

    Yields:
        Generator[Session, None, None]: A generator that yields the SQLAlchemy database session.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
                       