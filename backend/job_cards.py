from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/job-cards", tags=["job_cards"])

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/", response_model=schemas.JobCard, status_code=201)
async def create_job_card(
    job_card: schemas.JobCardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create new job card."""
    mechanic = db.query(models.User).filter(models.User.id == job_card.mechanic_id).first()
    if not mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    
    machine = db.query(models.Machine).filter(models.Machine.id == job_card.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    db_job_card = models.JobCard(
        mechanic_id=job_card.mechanic_id,
        machine_id=job_card.machine_id,
        problem_description=job_card.problem_description,
        status="open"
    )
    db.add(db_job_card)
    db.commit()
    db.refresh(db_job_card)
    return db_job_card

@router.get("/", response_model=List[schemas.JobCard])
async def list_job_cards(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
):
    """List job cards."""
    query = db.query(models.JobCard)
    if status:
        query = query.filter(models.JobCard.status == status)
    cards = query.offset(skip).limit(limit).all()
    return cards

@router.get("/{card_id}", response_model=schemas.JobCard)
async def get_job_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get job card by ID."""
    card = db.query(models.JobCard).filter(models.JobCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Job card not found")
    return card

@router.put("/{card_id}", response_model=schemas.JobCard)
async def update_job_card(
    card_id: int,
    card_update: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update job card."""
    card = db.query(models.JobCard).filter(models.JobCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Job card not found")
    
    valid_statuses = ["open", "in-progress", "completed", "on-hold"]
    if "status" in card_update and card_update["status"] not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    for key, value in card_update.items():
        if value is not None:
            setattr(card, key, value)
    db.commit()
    db.refresh(card)
    return card

@router.post("/{card_id}/upload-report", response_model=schemas.JobCard)
async def upload_job_card_report(
    card_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Upload work report image for job card."""
    card = db.query(models.JobCard).filter(models.JobCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Job card not found")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
    filename = timestamp + file.filename
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    try:
        contents = await file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    card.image_report_path = filepath
    db.commit()
    db.refresh(card)
    return card

@router.get("/mechanic/{mechanic_id}", response_model=List[schemas.JobCard])
async def get_mechanic_job_cards(
    mechanic_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all job cards for a mechanic."""
    cards = db.query(models.JobCard).filter(models.JobCard.mechanic_id == mechanic_id).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No job cards found for this mechanic")
    return cards

@router.delete("/{card_id}", status_code=204)
async def delete_job_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Delete job card (Manager/Admin only)."""
    card = db.query(models.JobCard).filter(models.JobCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Job card not found")
    db.delete(card)
    db.commit()
