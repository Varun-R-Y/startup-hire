import os
import pdfplumber
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.candidate.models import CandidateProfile
from app.parser.models import ParsedResume
from app.parser.schemas import ParsedResumeResponse
from app.parser.parser_service import parse_resume_text

router = APIRouter(prefix="/candidate", tags=["Parser"])


@router.post("/parse-resume", response_model=ParsedResumeResponse)
def parse_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extract raw plain text from the candidate's uploaded resume PDF, parse it,
    and save/update the ParsedResume entry.
    """
    # 1. Protect the endpoint using get_current_user. Only candidates may parse resumes.
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can parse resumes."
        )

    # 2. Retrieve the authenticated user's CandidateProfile.
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found."
        )

    # 3. If resume_path is NULL or empty, return HTTP 400 ("Resume not uploaded").
    if not profile.resume_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume not uploaded"
        )

    # 4. Check if file actually exists on disk.
    if not os.path.exists(profile.resume_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found on disk."
        )

    # 5. Extract plain text using pdfplumber.
    try:
        pages = []
        with pdfplumber.open(profile.resume_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
        extracted_text = "\n".join(pages)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading PDF file: {str(e)}"
        )

    # 6. Parse the extracted text using the resume parser service.
    parsed_fields = parse_resume_text(extracted_text)

    # 7. Check if a ParsedResume already exists for this candidate.
    parsed_resume = db.query(ParsedResume).filter(ParsedResume.candidate_profile_id == profile.id).first()

    if parsed_resume:
        # Update all extracted fields
        for key, val in parsed_fields.items():
            setattr(parsed_resume, key, val)
    else:
        # Create a new ParsedResume row
        parsed_resume = ParsedResume(
            candidate_profile_id=profile.id,
            **parsed_fields
        )
        db.add(parsed_resume)

    db.commit()
    db.refresh(parsed_resume)

    return parsed_resume

