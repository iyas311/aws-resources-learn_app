from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.aws.secrets import get_secret

# Get all secrets (including database credentials)
secrets = get_secret()

# Support both generic and db-specific secret keys
username = secrets.get("db_username") or secrets.get("username")
password = secrets.get("db_password") or secrets.get("password")
host = secrets.get("db_host") or secrets.get("host")
port = secrets.get("db_port") or secrets.get("port")
database = secrets.get("db_name") or secrets.get("database")

required_fields = {
    "db_username": username,
    "db_password": password,
    "db_host": host,
    "db_port": port,
    "db_name": database,
}
missing = [key for key, value in required_fields.items() if not value]
if missing:
    raise ValueError(f"Missing required database secret fields: {', '.join(missing)}")

# Build database URL from secrets
DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{username}:"
    f"{password}@"
    f"{host}:"
    f"{port}/"
    f"{database}"
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
