from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/quotations", tags=["quotations"])

@router.post("/", response_model=schemas.Quotation, status_code=201)
async def create_quotation(
    quotation: schemas.QuotationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Create new quotation (Manager/Admin only)."""
    db_quotation = models.Quotation(
        customer_name=quotation.customer_name,
        total_amount=quotation.total_amount,
        status="draft"
    )
    db.add(db_quotation)
    db.commit()
    db.refresh(db_quotation)
    return db_quotation

@router.get("/", response_model=List[schemas.Quotation])
async def list_quotations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    status: str = None
):
    """List quotations."""
    query = db.query(models.Quotation)
    if status:
        query = query.filter(models.Quotation.status == status)
    quotations = query.offset(skip).limit(limit).all()
    return quotations

@router.get("/{quotation_id}", response_model=schemas.Quotation)
async def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get quotation by ID."""
    quotation = db.query(models.Quotation).filter(models.Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation

@router.put("/{quotation_id}", response_model=schemas.Quotation)
async def update_quotation(
    quotation_id: int,
    quotation_update: schemas.QuotationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Update quotation (Manager/Admin only)."""
    db_quotation = db.query(models.Quotation).filter(models.Quotation.id == quotation_id).first()
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    for key, value in quotation_update.dict(exclude_unset=True).items():
        setattr(db_quotation, key, value)
    db.commit()
    db.refresh(db_quotation)
    return db_quotation

@router.put("/{quotation_id}/status", response_model=schemas.Quotation)
async def update_quotation_status(
    quotation_id: int,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Update quotation status (Manager/Admin only)."""
    quotation = db.query(models.Quotation).filter(models.Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    valid_statuses = ["draft", "sent", "approved", "rejected", "invoiced"]
    if status_update.get("status") not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(valid_statuses)}"
        )
    
    quotation.status = status_update["status"]
    db.commit()
    db.refresh(quotation)
    return quotation

@router.get("/by-customer/{customer_name}", response_model=List[schemas.Quotation])
async def get_quotations_by_customer(
    customer_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get quotations for a specific customer."""
    quotations = db.query(models.Quotation).filter(
        models.Quotation.customer_name == customer_name
    ).all()
    if not quotations:
        raise HTTPException(status_code=404, detail="No quotations found for this customer")
    return quotations

@router.delete("/{quotation_id}", status_code=204)
async def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Delete quotation (Manager/Admin only)."""
    quotation = db.query(models.Quotation).filter(models.Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    invoice = db.query(models.Invoice).filter(models.Invoice.quotation_id == quotation_id).first()
    if invoice:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete quotation that has an associated invoice"
        )
    
    db.delete(quotation)
    db.commit()
