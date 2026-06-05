from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.aws.secrets import get_secret

# Get all secrets (including database credentials)
secrets = get_secret()

# Build database URL from secrets
DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{secrets['username']}:"
    f"{secrets['password']}@"
    f"{secrets['host']}:"
    f"{secrets['port']}/"
    f"{secrets['database']}"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Test connection before using
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
