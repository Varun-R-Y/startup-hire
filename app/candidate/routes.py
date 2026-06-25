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
