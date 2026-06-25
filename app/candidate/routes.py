from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.candidate.models import CandidateProfile
from app.candidate.schemas import CandidateProfileCreate, CandidateProfileResponse

router = APIRouter(prefix="/candidate", tags=["Candidate"])

@router.post("/profile", response_model=CandidateProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_in: CandidateProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a professional profile for the currently authenticated candidate.
    """
    # Verify the authenticated user is a candidate
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can create a candidate profile."
        )
    # 1. Verify that the user does not already have a profile
    existing_profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Candidate profile already exists for this user."
        )

    # 2. Instantiate and persist the CandidateProfile using the logged-in user's ID
    new_profile = CandidateProfile(
        user_id=current_user.id,
        **profile_in.model_dump()
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get("/profile", response_model=CandidateProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the candidate profile of the authenticated user.
    """
    # 1. Verify the authenticated user is a candidate
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can access a candidate profile."
        )

    # 2. Retrieve the profile from the database
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found."
        )

    return profile


@router.put("/profile", response_model=CandidateProfileResponse)
def update_profile(
    profile_in: CandidateProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the candidate profile of the authenticated user.
    """
    # 1. Verify the authenticated user is a candidate
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can update a candidate profile."
        )

    # 2. Retrieve the existing profile from the database
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found."
        )

    # 3. Update all editable fields from the Pydantic schema
    for key, value in profile_in.model_dump().items():
        setattr(profile, key, value)

    # 4. Save changes to PostgreSQL and refresh the object
    db.commit()
    db.refresh(profile)

    return profile


