from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.post("/", response_model=schemas.Inventory, status_code=201)
async def create_inventory(
    inventory: schemas.InventoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Create new inventory item (Manager/Admin only)."""
    existing = db.query(models.InventoryItem).filter(
        models.InventoryItem.part_number == inventory.part_number
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Part number already exists"
        )
    
    db_inventory = models.InventoryItem(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

@router.get("/", response_model=List[schemas.Inventory])
async def list_inventory(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """List all inventory items."""
    items = db.query(models.InventoryItem).offset(skip).limit(limit).all()
    return items

@router.get("/{item_id}", response_model=schemas.Inventory)
async def get_inventory(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get inventory item by ID."""
    item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item

@router.put("/{item_id}", response_model=schemas.Inventory)
async def update_inventory(
    item_id: int,
    inventory_update: schemas.InventoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Update inventory item (Manager/Admin only)."""
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    for key, value in inventory_update.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}", status_code=204)
async def delete_inventory(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Delete inventory item (Manager/Admin only)."""
    item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    db.delete(item)
    db.commit()

@router.get("/search/by-category", response_model=List[schemas.Inventory])
async def search_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Search inventory items by category."""
    items = db.query(models.InventoryItem).filter(
        models.InventoryItem.category == category
    ).all()
    if not items:
        raise HTTPException(status_code=404, detail="No items found in this category")
    return items

@router.get("/search/low-stock", response_model=List[schemas.Inventory])
async def get_low_stock(
    threshold: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get items with stock below threshold."""
    items = db.query(models.InventoryItem).filter(
        models.InventoryItem.stock_level < threshold
    ).all()
    return items
