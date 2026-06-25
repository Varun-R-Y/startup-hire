from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.models import User
from app.auth.schemas import UserCreate, UserResponse, Token
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user in the system.
    """
    # 1. Check if email already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )
    
    # 2. Hash password
    hashed_password = hash_password(user_in.password)
    
    # 3. Create User model instance
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password,
        role=user_in.role
    )
    
    # 4. Save to PostgreSQL database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 5. Return the serialized UserResponse
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.
    """
    # 1. Find user by email (using form_data.username)
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # 2. Verify password (using form_data.password)
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # 3. Generate access token
    access_token = create_access_token(data={"sub": user.email,"user_id": user.id, "role": user.role})
    
    # 4. Return token response
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user