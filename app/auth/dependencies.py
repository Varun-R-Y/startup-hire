from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.jwt_handler import verify_access_token
from app.auth.models import User

# Initialize OAuth2PasswordBearer scheme pointing to the login route.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Retrieves the current authenticated user from the database.
    
    Reads the JWT from the Authorization Bearer token, verifies it using
    verify_access_token(), extracts the user_id, fetches the user from PostgreSQL,
    and returns the User object.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode and verify the JWT access token
    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception

    # Extract the user_id from the payload
    user_id = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    # Query the database for the user
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user
