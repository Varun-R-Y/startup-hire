from passlib.context import CryptContext

# Set up CryptContext with bcrypt hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    """
    Verifies a plain-text password against a hashed password.
    """
    return pwd_context.verify(password, hashed_password)
