from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=schemas.User, status_code=201)
async def register_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Register a new user (Admin only)."""
    db_user = auth.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        department=user.department,
        hashed_password=hashed_password,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=schemas.Token)
async def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login user and get JWT token."""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "department": user.department,
            "is_active": user.is_active
        }
    }

@router.get("/me", response_model=schemas.User)
async def get_current_user_info(current_user: models.User = Depends(auth.get_current_active_user)):
    """Get current authenticated user's profile."""
    return current_user

@router.get("/", response_model=list[schemas.User])
async def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """List all users (Manager/Admin only)."""
    users = db.query(models.User).all()
    return users

@router.get("/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Get user by ID (Manager/Admin only)."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Update user details (Manager/Admin only)."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.username and user_update.username != db_user.username:
        existing = db.query(models.User).filter(models.User.username == user_update.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_manager_user)
):
    """Delete user (Manager/Admin only)."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
