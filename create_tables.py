import sys
from app.database import Base, engine
# Import all models to ensure they are registered on the Base metadata
from app.auth.models import User
from app.candidate.models import CandidateProfile
from app.startup.models import StartupProfile


def create_tables():
    """
    Creates all database tables registered with the SQLAlchemy Base metadata.
    """
    print("Connecting to the database and creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error occurred while creating tables: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
