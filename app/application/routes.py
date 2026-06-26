from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.candidate.models import CandidateProfile
from app.startup.models import StartupProfile
from app.jobs.models import JobPosting
from app.application.models import Application
from app.application.schemas import ApplicationResponse, RankedCandidateResponse
from app.parser.models import ParsedResume
from app.matching.service import calculate_match_score

router = APIRouter(tags=["Application"])


@router.post("/candidate/apply/{job_id}", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a job application for the authenticated candidate.
    """
    # 1. Enforce Candidate only role
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can apply to jobs."
        )

    # 2. Verify CandidateProfile exists
    candidate_profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not candidate_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found."
        )

    # 3. Verify JobPosting exists
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found."
        )

    # 4. Prevent duplicate applications (409 Conflict)
    existing_app = db.query(Application).filter(
        Application.candidate_profile_id == candidate_profile.id,
        Application.job_posting_id == job_id
    ).first()
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this job."
        )

    # 5. Create new Application
    new_app = Application(
        candidate_profile_id=candidate_profile.id,
        job_posting_id=job_id
    )

    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return new_app


@router.get("/candidate/applications", response_model=list[ApplicationResponse])
def get_candidate_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all job applications submitted by the authenticated candidate.
    """
    # 1. Enforce Candidate only role
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can retrieve their applications."
        )

    # 2. Verify CandidateProfile exists
    candidate_profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not candidate_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found."
        )

    # 3. Fetch applications
    apps = db.query(Application).filter(Application.candidate_profile_id == candidate_profile.id).all()
    return apps


@router.get("/startup/jobs/{job_id}/applications", response_model=list[ApplicationResponse])
def get_job_applications(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all applications for a specific job posting. Only accessible by the owning startup.
    """
    # 1. Enforce Startup only role
    if current_user.role != "startup":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only startups can view job applications."
        )

    # 2. Retrieve StartupProfile
    startup_profile = db.query(StartupProfile).filter(StartupProfile.user_id == current_user.id).first()
    if not startup_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found."
        )

    # 3. Retrieve JobPosting and verify ownership
    job = db.query(JobPosting).filter(
        JobPosting.id == job_id,
        JobPosting.startup_profile_id == startup_profile.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found or does not belong to this startup."
        )

    # 4. Fetch applications for the job
    apps = db.query(Application).filter(Application.job_posting_id == job_id).all()
    return apps


@router.get("/startup/jobs/{job_id}/rank-candidates", response_model=list[RankedCandidateResponse])
def rank_candidates(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rank all candidates who applied to a job posting, sorted descending by match score.
    """
    # 1. Protect and verify user role
    if current_user.role != "startup":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only startups can view candidate rankings."
        )

    # 2. Retrieve StartupProfile
    startup_profile = db.query(StartupProfile).filter(StartupProfile.user_id == current_user.id).first()
    if not startup_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found."
        )

    # 3. Retrieve JobPosting and verify ownership
    job = db.query(JobPosting).filter(
        JobPosting.id == job_id,
        JobPosting.startup_profile_id == startup_profile.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found or does not belong to this startup."
        )

    # 4. Retrieve all Application records for that job
    apps = db.query(Application).filter(Application.job_posting_id == job_id).all()

    ranked_list = []
    for app in apps:
        # Load CandidateProfile
        candidate_profile = app.candidate_profile
        
        # Load ParsedResume (one-to-one relationship)
        parsed_resume = candidate_profile.parsed_resume
        if parsed_resume is None:
            continue

        # Calculate matching score using the service
        score_details = calculate_match_score(job, candidate_profile, parsed_resume)

        # Build response item
        ranked_list.append({
            "candidate_profile_id": candidate_profile.id,
            "candidate_name": candidate_profile.user.name,
            "score": score_details["score"],
            "skill_score": score_details["skill_score"],
            "experience_score": score_details["experience_score"],
            "location_score": score_details["location_score"],
            "matched_skills": score_details["matched_skills"],
            "missing_skills": score_details["missing_skills"]
        })

    # Sort descending by score, breaking ties using skill score, then experience score
    ranked_list.sort(
        key=lambda x: (
            x["score"],
            x["skill_score"],
            x["experience_score"]
        ),
        reverse=True
    )

    return ranked_list

