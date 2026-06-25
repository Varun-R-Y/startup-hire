from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.startup.models import StartupProfile
from app.startup.schemas import StartupProfileCreate, StartupProfileResponse

router = APIRouter(prefix="/startup", tags=["Startup"])

@router.post("/profile", response_model=StartupProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_in: StartupProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a professional profile for the currently authenticated startup.
    """
    # 1. Verify the authenticated user has the "startup" role
    if current_user.role != "startup":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only startup users can create a startup profile."
        )

    # 2. Check if the user already has a startup profile
    existing_profile = db.query(StartupProfile).filter(StartupProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Startup profile already exists for this user."
        )

    # 3. Create profile instance using values from profile_in and current_user.id
    new_profile = StartupProfile(
        user_id=current_user.id,
        **profile_in.model_dump()
    )

    # 4. Save to PostgreSQL database
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get("/profile", response_model=StartupProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the startup profile of the authenticated user.
    """
    # 1. Verify the authenticated user is a startup
    if current_user.role != "startup":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only startup users can access a startup profile."
        )

    # 2. Retrieve the profile from the database
    profile = db.query(StartupProfile).filter(StartupProfile.user_id == current_user.id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found."
        )

    return profile


@router.put("/profile", response_model=StartupProfileResponse)
def update_profile(
    profile_in: StartupProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the startup profile of the authenticated user.
    """
    # 1. Verify the authenticated user is a startup
    if current_user.role != "startup":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only startup users can update a startup profile."
        )

    # 2. Retrieve the existing profile from the database
    profile = db.query(StartupProfile).filter(StartupProfile.user_id == current_user.id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found."
        )

    # 3. Update all editable fields from the Pydantic schema
    for key, value in profile_in.model_dump().items():
        setattr(profile, key, value)

    # 4. Save changes to PostgreSQL and refresh the object
    db.commit()
    db.refresh(profile)

    return profile


