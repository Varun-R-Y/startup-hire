from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.startup.models import StartupProfile
from app.jobs.models import JobPosting
from app.jobs.schemas import JobPostingCreate, JobPostingResponse

router = APIRouter(prefix="/startup", tags=["Jobs"])


@router.post("/jobs", response_model=JobPostingResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobPostingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new job posting for the authenticated startup.
    """
    # 1. Protect using get_current_user and check role
    if current_user.role != "startup":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only startups can create job postings."
        )

    # 2. Retrieve the authenticated user's StartupProfile
    profile = db.query(StartupProfile).filter(StartupProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found."
        )

    # 3. Create a JobPosting using the profile's ID and model fields
    new_job = JobPosting(
        startup_profile_id=profile.id,
        **job_in.model_dump()
    )

    # 4. Save to PostgreSQL
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@router.get("/jobs", response_model=list[JobPostingResponse])
def get_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all job postings belonging to the authenticated startup.
    """
    # 1. Protect and verify user role
    if current_user.role != "startup":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only startups can retrieve their job postings."
        )

    # 2. Retrieve StartupProfile
    profile = db.query(StartupProfile).filter(StartupProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found."
        )

    # 3. Retrieve all job postings belonging to this startup
    jobs = db.query(JobPosting).filter(JobPosting.startup_profile_id == profile.id).all()
    return jobs


@router.put("/jobs/{job_id}", response_model=JobPostingResponse)
def update_job(
    job_id: int,
    job_in: JobPostingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing job posting belonging to the authenticated startup.
    """
    # 1. Protect and verify user role
    if current_user.role != "startup":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only startups can update their job postings."
        )

    # 2. Retrieve StartupProfile
    profile = db.query(StartupProfile).filter(StartupProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found."
        )

    # 3. Retrieve specified JobPosting belonging to that startup
    job = db.query(JobPosting).filter(
        JobPosting.id == job_id,
        JobPosting.startup_profile_id == profile.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found."
        )

    # 4. Update all editable fields from JobPostingCreate
    for key, value in job_in.model_dump().items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)

    return job


@router.delete("/jobs/{job_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a job posting belonging to the authenticated startup.
    """
    # 1. Protect and verify user role
    if current_user.role != "startup":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only startups can delete their job postings."
        )

    # 2. Retrieve StartupProfile
    profile = db.query(StartupProfile).filter(StartupProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup profile not found."
        )

    # 3. Retrieve specified JobPosting belonging to that startup
    job = db.query(JobPosting).filter(
        JobPosting.id == job_id,
        JobPosting.startup_profile_id == profile.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found."
        )

    # 4. Delete the job posting
    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully."
    }

