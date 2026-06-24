from app.database import Base, engine
from app.auth.models import User  # Must import models to register them on Base.metadata

def create_tables() -> None:
    """
    Creates all database tables defined in the SQLAlchemy metadata.
    """
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables initialized successfully!")

if __name__ == "__main__":
    create_tables()
