from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.post("/", response_model=schemas.Invoice, status_code=201)
async def create_invoice(
    invoice: schemas.InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Create new invoice from quotation (Manager/Admin only)."""
    quotation = db.query(models.Quotation).filter(
        models.Quotation.id == invoice.quotation_id
    ).first()
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    existing_invoice = db.query(models.Invoice).filter(
        models.Invoice.quotation_id == invoice.quotation_id
    ).first()
    if existing_invoice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice already exists for this quotation"
        )
    
    db_invoice = models.Invoice(
        quotation_id=invoice.quotation_id,
        customer_name=quotation.customer_name,
        total_amount=quotation.total_amount,
        status="issued"
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@router.get("/", response_model=List[schemas.Invoice])
async def list_invoices(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """List all invoices."""
    invoices = db.query(models.Invoice).offset(skip).limit(limit).all()
    return invoices

@router.get("/{invoice_id}", response_model=schemas.Invoice)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get invoice by ID."""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.put("/{invoice_id}/status", response_model=schemas.Invoice)
async def update_invoice_status(
    invoice_id: int,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Update invoice status (Manager/Admin only)."""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    valid_statuses = ["issued", "paid", "overdue", "cancelled"]
    if status_update.get("status") not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(valid_statuses)}"
        )
    
    invoice.status = status_update["status"]
    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("/by-customer/{customer_name}", response_model=List[schemas.Invoice])
async def get_invoices_by_customer(
    customer_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get invoices for a specific customer."""
    invoices = db.query(models.Invoice).filter(
        models.Invoice.customer_name == customer_name
    ).all()
    if not invoices:
        raise HTTPException(status_code=404, detail="No invoices found for this customer")
    return invoices

@router.get("/by-status/{status}", response_model=List[schemas.Invoice])
async def get_invoices_by_status(
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get invoices by status."""
    invoices = db.query(models.Invoice).filter(models.Invoice.status == status).all()
    if not invoices:
        raise HTTPException(status_code=404, detail="No invoices found with this status")
    return invoices
