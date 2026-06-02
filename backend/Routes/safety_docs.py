from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/safety-docs", tags=["safety_docs"])

@router.post("/", response_model=schemas.SafetyDocument, status_code=201)
async def create_safety_document(
    doc: schemas.SafetyDocumentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create new safety document for a job card."""
    job_card = db.query(models.JobCard).filter(
        models.JobCard.id == doc.job_card_id
    ).first()
    if not job_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job card not found"
        )
    
    db_doc = models.SafetyDocument(
        job_card_id=doc.job_card_id,
        title=doc.title,
        is_signed=0
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

@router.get("/", response_model=List[schemas.SafetyDocument])
async def list_safety_documents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """List all safety documents."""
    docs = db.query(models.SafetyDocument).offset(skip).limit(limit).all()
    return docs

@router.get("/{doc_id}", response_model=schemas.SafetyDocument)
async def get_safety_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get safety document by ID."""
    doc = db.query(models.SafetyDocument).filter(models.SafetyDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Safety document not found")
    return doc

@router.post("/{doc_id}/sign", response_model=schemas.SafetyDocument)
async def sign_safety_document(
    doc_id: int,
    signature_data: schemas.SafetyDocumentSign,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Sign a safety document (Manager/Admin only)."""
    doc = db.query(models.SafetyDocument).filter(models.SafetyDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Safety document not found")
    
    doc.is_signed = 1
    doc.manager_signature = signature_data.signature_data
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/job-card/{job_card_id}", response_model=List[schemas.SafetyDocument])
async def get_safety_documents_by_job_card(
    job_card_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all safety documents for a job card."""
    docs = db.query(models.SafetyDocument).filter(
        models.SafetyDocument.job_card_id == job_card_id
    ).all()
    if not docs:
        raise HTTPException(status_code=404, detail="No safety documents found for this job card")
    return docs

@router.delete("/{doc_id}", status_code=204)
async def delete_safety_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Delete safety document (Manager/Admin only)."""
    doc = db.query(models.SafetyDocument).filter(models.SafetyDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Safety document not found")
    db.delete(doc)
    db.commit()

